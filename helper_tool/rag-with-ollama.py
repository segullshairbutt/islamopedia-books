#!/usr/bin/env python3
"""
RAG Pipeline with Ollama

This script creates a RAG (Retrieval-Augmented Generation) pipeline that:
1. Scans all Markdown files in a specified book directory
2. Creates embeddings using a multilingual embedding model
3. Stores embeddings in ChromaDB
4. Allows querying the knowledge base using Ollama LM
"""

import os
import re
import glob
import typer
from typing import List, Optional, Dict, Any
from langchain.text_splitter import MarkdownTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

app = typer.Typer()

# Define constants
DEFAULT_COLLECTION_NAME = "book_collection"
DEFAULT_CHUNK_SIZE = 300  # Smaller chunks for more granular retrieval
DEFAULT_CHUNK_OVERLAP = 100  # Increased overlap to avoid missing context between chunks
DEFAULT_EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
DEFAULT_LLM_MODEL = "mistral"
DEFAULT_PERSIST_DIRECTORY = "./chroma_db"
DEFAULT_RETRIEVAL_K = 10  # Increased number of chunks to retrieve

def setup_embedding_function(model_name: str = DEFAULT_EMBEDDING_MODEL):
    """Set up and return the embedding function using HuggingFace models."""
    return HuggingFaceEmbeddings(model_name=model_name)

def load_and_process_markdown_files(book_path: str, 
                                    chunk_size: int = DEFAULT_CHUNK_SIZE, 
                                    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP) -> List[Dict[str, Any]]:
    """Load all markdown files from a directory and process them into chunks."""
    print(f"Scanning for markdown files in: {book_path}")
    
    # Find all markdown files
    markdown_files = []
    for ext in ["*.md", "*.rtl.md"]:
        pattern = os.path.join(book_path, "**", ext)
        markdown_files.extend(glob.glob(pattern, recursive=True))
    
    if not markdown_files:
        print(f"No markdown files found in {book_path}")
        return []
    
    print(f"Found {len(markdown_files)} markdown files")
    
    # Sort files to maintain logical ordering (assuming filenames indicate order)
    markdown_files.sort()
    
    # Process each file
    text_splitter = MarkdownTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    documents = []
    
    # Track book-level metadata
    book_name = os.path.basename(os.path.normpath(book_path))
    total_chunks = 0
    
    for file_path in markdown_files:
        try:
            # Get relative path for metadata
            rel_path = os.path.relpath(file_path, book_path)
            
            # Try to extract chapter/section information from filename
            file_name = os.path.basename(file_path)
            match = re.search(r'chap_(\d+)', file_name)
            chapter_num = match.group(1) if match else "unknown"
            
            # Load the file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract title from markdown if available (assuming first heading is title)
            title_match = re.search(r'#\s+([^\n]+)', content)
            title = title_match.group(1).strip() if title_match else file_name
            
            # Split the content into chunks
            chunks = text_splitter.split_text(content)
            
            # Create document objects with rich metadata
            for i, chunk in enumerate(chunks):
                documents.append({
                    "page_content": chunk,
                    "metadata": {
                        "source": rel_path,
                        "chunk": i,
                        "file_path": file_path,
                        "title": title,
                        "book": book_name,
                        "chapter": chapter_num,
                        "chunk_id": f"{chapter_num}_{i}",
                        "total_chunks_in_file": len(chunks)
                    }
                })
                total_chunks += 1
                
            print(f"Processed: {rel_path} - {len(chunks)} chunks")
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
    
    print(f"Total chunks created: {total_chunks}")
    return documents

def create_vector_store(documents: List[Dict[str, Any]], 
                        embedding_function, 
                        collection_name: str = DEFAULT_COLLECTION_NAME, 
                        persist_directory: str = DEFAULT_PERSIST_DIRECTORY) -> Chroma:
    """Create and return a Chroma vector store with the documents."""
    # Extract texts and metadatas
    texts = [doc["page_content"] for doc in documents]
    metadatas = [doc["metadata"] for doc in documents]
    
    # Create and persist the vector store
    vector_store = Chroma.from_texts(
        texts=texts,
        embedding=embedding_function,
        metadatas=metadatas,
        persist_directory=persist_directory,
        collection_name=collection_name
    )
    
    return vector_store

def load_vector_store(embedding_function, 
                     collection_name: str = DEFAULT_COLLECTION_NAME,
                     persist_directory: str = DEFAULT_PERSIST_DIRECTORY) -> Optional[Chroma]:
    """Load an existing Chroma vector store."""
    try:
        vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embedding_function,
            persist_directory=persist_directory
        )
        return vector_store
    except Exception as e:
        print(f"Error loading vector store: {e}")
        return None

def setup_qa_chain(vector_store, model_name: str = DEFAULT_LLM_MODEL):
    """Set up and return a QA chain using Ollama and the vector store."""
    # Initialize Ollama LLM with specific parameters for detailed responses
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    
    llm = Ollama(
        model=model_name,
        callback_manager=callback_manager,
        temperature=0.1,  # Lower temperature for more focused responses
        num_ctx=4096,     # Increase context window
        num_predict=2048, # Allow for longer generations
        repeat_penalty=1.1, # Reduce repetition
        top_k=10,         # Consider top 10 tokens at each step
        top_p=0.9,        # Sample from top 90% probability mass
    )
    
    # Create a custom prompt template that explicitly requests detailed answers
    prompt_template = """You are a knowledgeable assistant that provides detailed, comprehensive answers STRICTLY based on the provided context from the indexed book.

    IMPORTANT INSTRUCTIONS:
    1. ONLY use information that is explicitly present in the provided context.
    2. DO NOT introduce any information from your general knowledge unless explicitly asked by the user.
    3. If the answer cannot be fully derived from the context, state clearly: "Based on the available book content, I cannot find complete information about this question."
    4. Do not make up or infer information that is not directly supported by the context.
    5. If asked about something outside the book's scope, say: "This question appears to be outside the scope of the indexed book content."

    Your answers should be thorough and well-structured, with:
    - Complete explanations covering all aspects found in the context
    - Direct quotes from the book when appropriate
    - Clear organization using paragraphs and bullet points when appropriate
    - Explicit citations to specific chapters/sections of the book

    Context (ONLY use this information for your answer):
    {context}

    Question: {question}

    Detailed Answer (using ONLY information from the indexed book):"""
    
    PROMPT = PromptTemplate(
        template=prompt_template,
        input_variables=["context", "question"]
    )
    
    # Create the QA chain with more retrieved documents and better search
    retriever = vector_store.as_retriever(
        search_type="mmr",  # Maximum Marginal Relevance for diversity
        search_kwargs={
            "k": DEFAULT_RETRIEVAL_K,  # Retrieve more chunks
            "fetch_k": DEFAULT_RETRIEVAL_K * 3,  # Consider a larger set before selecting diverse subset
            "lambda_mult": 0.7,  # Balance between relevance and diversity (higher = more relevance)
        }
    )
    
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # Simple approach: stuff all retrieved docs into prompt
        retriever=retriever,
        chain_type_kwargs={"prompt": PROMPT}
    )
    
    return qa_chain

@app.command()
def index(
    book_path: str = typer.Argument(..., help="Path to the book directory containing markdown files"),
    collection_name: str = typer.Option(DEFAULT_COLLECTION_NAME, help="Name of the ChromaDB collection"),
    chunk_size: int = typer.Option(DEFAULT_CHUNK_SIZE, help="Size of text chunks"),
    chunk_overlap: int = typer.Option(DEFAULT_CHUNK_OVERLAP, help="Overlap between text chunks"),
    embedding_model: str = typer.Option(DEFAULT_EMBEDDING_MODEL, help="HuggingFace embedding model to use"),
    persist_directory: str = typer.Option(DEFAULT_PERSIST_DIRECTORY, help="Directory to persist the ChromaDB")
):
    """Index all markdown files in a book directory and store embeddings in ChromaDB."""
    print(f"Indexing book: {book_path}")
    print(f"Using embedding model: {embedding_model}")
    
    # Setup embedding function
    embedding_function = setup_embedding_function(embedding_model)
    
    # Load and process markdown files
    documents = load_and_process_markdown_files(book_path, chunk_size, chunk_overlap)
    
    if not documents:
        print("No documents to index. Exiting.")
        return
    
    # Create vector store
    vector_store = create_vector_store(
        documents=documents,
        embedding_function=embedding_function,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    
    print(f"Successfully indexed {len(documents)} chunks into ChromaDB collection '{collection_name}'")
    print(f"Vector store persisted at: {persist_directory}")

@app.command()
def query(
    query_text: str = typer.Argument(..., help="Query text to search for"),
    collection_name: str = typer.Option(DEFAULT_COLLECTION_NAME, help="Name of the ChromaDB collection"),
    embedding_model: str = typer.Option(DEFAULT_EMBEDDING_MODEL, help="HuggingFace embedding model to use"),
    llm_model: str = typer.Option(DEFAULT_LLM_MODEL, help="Ollama model to use"),
    persist_directory: str = typer.Option(DEFAULT_PERSIST_DIRECTORY, help="Directory where ChromaDB is persisted"),
    k: int = typer.Option(DEFAULT_RETRIEVAL_K, help="Number of documents to retrieve"),
    temperature: float = typer.Option(0.1, help="Temperature for LLM generation (0.0-1.0)")
):
    """Query the indexed book using Ollama LLM."""
    print(f"Querying collection '{collection_name}' with: {query_text}")
    print(f"Using embedding model: {embedding_model}")
    print(f"Using LLM model: {llm_model} with temperature {temperature}")
    print(f"Retrieving {k} document chunks for context")
    
    # Setup embedding function
    embedding_function = setup_embedding_function(embedding_model)
    
    # Load vector store
    vector_store = load_vector_store(
        embedding_function=embedding_function,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    
    if not vector_store:
        print(f"Could not load vector store from {persist_directory}. Please index a book first.")
        return
    
    # Setup QA chain
    qa_chain = setup_qa_chain(vector_store, llm_model)
    
    # Get response
    print("\nQuerying LLM...")
    print("This may take a moment as the model generates a detailed response...")
    response = qa_chain.invoke({"query": query_text})
    
    print("\n--- Response ---")
    print(response["result"])
    
    # Also show the retrieved documents for reference
    print("\n--- Retrieved Documents ---")
    docs = vector_store.similarity_search(
        query_text, 
        k=k,
        fetch_k=k*3,  # Fetch more and select diverse subset
        lambda_mult=0.7  # Balance between relevance and diversity
    )
    
    # Print document sources in a more structured way
    chapters_seen = set()
    print("\nSources by Chapter:")
    for i, doc in enumerate(docs):
        chapter = doc.metadata.get('chapter', 'unknown')
        title = doc.metadata.get('title', 'unknown')
        source = doc.metadata.get('source', 'unknown')
        
        if chapter not in chapters_seen:
            print(f"\nChapter {chapter}: {title}")
            chapters_seen.add(chapter)
        
        print(f"  - Document {i+1}: {source} (Chunk {doc.metadata.get('chunk', 'unknown')})")
    
    # Print the actual content of the retrieved documents
    print("\nDocument Content:")
    for i, doc in enumerate(docs):
        print(f"\nDocument {i+1}:")
        print(f"Source: {doc.metadata.get('source', 'unknown')}")
        print(f"Chapter: {doc.metadata.get('chapter', 'unknown')}")
        print(f"Title: {doc.metadata.get('title', 'unknown')}")
        print(f"Content Preview: {doc.page_content[:200]}...")

@app.command()
def interactive(
    collection_name: str = typer.Option(DEFAULT_COLLECTION_NAME, help="Name of the ChromaDB collection"),
    embedding_model: str = typer.Option(DEFAULT_EMBEDDING_MODEL, help="HuggingFace embedding model to use"),
    llm_model: str = typer.Option(DEFAULT_LLM_MODEL, help="Ollama model to use"),
    persist_directory: str = typer.Option(DEFAULT_PERSIST_DIRECTORY, help="Directory where ChromaDB is persisted"),
    temperature: float = typer.Option(0.1, help="Temperature for LLM generation (0.0-1.0)")
):
    """Start an interactive query session."""
    print(f"Starting interactive query session for collection '{collection_name}'")
    print(f"Using embedding model: {embedding_model}")
    print(f"Using LLM model: {llm_model} with temperature {temperature}")
    print("Type 'exit' or 'quit' to end the session")
    
    # Setup embedding function
    embedding_function = setup_embedding_function(embedding_model)
    
    # Load vector store
    vector_store = load_vector_store(
        embedding_function=embedding_function,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    
    if not vector_store:
        print(f"Could not load vector store from {persist_directory}. Please index a book first.")
        return
    
    # Setup QA chain
    qa_chain = setup_qa_chain(vector_store, llm_model)
    
    # Interactive loop
    while True:
        query_text = input("\nEnter your query (or 'exit'/'quit' to end): ")
        
        if query_text.lower() in ["exit", "quit"]:
            print("Exiting interactive session")
            break
            
        if not query_text.strip():
            continue
            
        # Get response
        print("Querying LLM...")
        print("This may take a moment as the model generates a detailed response...")
        response = qa_chain.invoke({"query": query_text})
        
        print("\n--- Response ---")
        print(response["result"])

@app.command()
def analyze_collection(
    collection_name: str = typer.Option(DEFAULT_COLLECTION_NAME, help="Name of the ChromaDB collection"),
    embedding_model: str = typer.Option(DEFAULT_EMBEDDING_MODEL, help="HuggingFace embedding model to use"),
    persist_directory: str = typer.Option(DEFAULT_PERSIST_DIRECTORY, help="Directory where ChromaDB is persisted")
):
    """Analyze the indexed collection to understand what content is available."""
    print(f"Analyzing collection '{collection_name}'...")
    
    # Setup embedding function
    embedding_function = setup_embedding_function(embedding_model)
    
    # Load vector store
    vector_store = load_vector_store(
        embedding_function=embedding_function,
        collection_name=collection_name,
        persist_directory=persist_directory
    )
    
    if not vector_store:
        print(f"Could not load vector store from {persist_directory}. Please index a book first.")
        return
    
    # Get all documents
    docs = vector_store.similarity_search("", k=10000)  # Get as many as possible
    
    if not docs:
        print("No documents found in the collection.")
        return
    
    # Analyze sources
    sources = {}
    chapters = {}
    total_chunks = len(docs)
    
    for doc in docs:
        source = doc.metadata.get('source', 'unknown')
        chapter = doc.metadata.get('chapter', 'unknown')
        
        sources[source] = sources.get(source, 0) + 1
        chapters[chapter] = chapters.get(chapter, 0) + 1
    
    # Print summary
    print(f"\n--- Collection Analysis ---")
    print(f"Total documents: {total_chunks}")
    print(f"Unique sources: {len(sources)}")
    print(f"Chapters covered: {len(chapters)}")
    
    print("\nChapter distribution:")
    # Fixed sorting to handle non-numeric chapter identifiers
    def chapter_sort_key(item):
        chapter = item[0]
        try:
            # Try to convert to integer for numeric sorting
            return (0, int(chapter))
        except (ValueError, TypeError):
            # If not a number, sort alphabetically but after all numbers
            return (1, str(chapter))
    
    for chapter, count in sorted(chapters.items(), key=chapter_sort_key):
        print(f"  Chapter {chapter}: {count} chunks ({count/total_chunks*100:.1f}%)")
    
    print("\nTop 10 sources by chunk count:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {source}: {count} chunks")
    
    # Calculate approximate token count
    approx_tokens = sum(len(doc.page_content.split()) * 1.3 for doc in docs)
    print(f"\nApproximate total tokens: {int(approx_tokens)}")
    print(f"Average tokens per chunk: {int(approx_tokens/total_chunks) if total_chunks else 0}")

if __name__ == "__main__":
    app()

