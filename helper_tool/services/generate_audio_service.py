import os
import openai
import tempfile
import tiktoken
import zipfile
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")


def get_openai_usage_info():
    """
    Get OpenAI usage/billing information.
    Note: This requires billing API access which may not be available for all accounts.
    
    Returns:
        dict: Dictionary containing usage information or error
    """
    try:
        # Note: OpenAI doesn't provide a direct usage API for all accounts
        # This is a placeholder that returns helpful information
        return {
            "success": False,
            "message": "OpenAI usage tracking requires billing API access",
            "note": "Monitor your usage at https://platform.openai.com/usage",
            "tip": "TTS costs approximately $15 per 1M characters"
        }
    except Exception as e:
        print(f"Error fetching OpenAI usage: {e}")
        return {"success": False, "error": str(e)}


def split_text_by_tokens(text, max_tokens=1500, encoding_name="cl100k_base"):
    enc = tiktoken.get_encoding(encoding_name)
    tokens = enc.encode(text)
    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_text = enc.decode(tokens[start:end])
        if end < len(tokens):
            # Try to split at the last period (.) or Urdu/Arabic full stop (۔)
            last_period = chunk_text.rfind(".")
            last_urdu = chunk_text.rfind("۔")
            # Pick the last one that occurs
            split_at = max(last_period, last_urdu)
            if split_at != -1:
                chunk_text = chunk_text[:split_at+1]
                end = start + len(enc.encode(chunk_text))
        chunks.append(chunk_text.strip())
        start = end
    return [c for c in chunks if c]


def generate_openai_tts(
    text, model, voice, speed, instructions, progress_callback=None
):
    """
    Calls OpenAI TTS API and returns the path to a zip file containing all mp3 chunks.
    Splits text into chunks of ≤1900 tokens, splitting at the last period.
    """
    chunks = split_text_by_tokens(text)
    total = len(chunks)
    print(f"[TTS] Total splits/chunks to generate: {total}")
    temp_dir = tempfile.TemporaryDirectory()
    mp3_paths = []
    permanent_chunk_paths = []
    
    for idx, chunk in enumerate(chunks, start=1):
        print(f"[TTS] Generating chunk {idx}/{total} ...")
        response = openai.audio.speech.create(
            model=model,
            voice=voice,
            input=chunk,
            speed=float(speed),
            response_format="mp3",
            instructions=instructions,
        )
        mp3_path = os.path.join(temp_dir.name, f"chunk_{idx}.mp3")
        with open(mp3_path, "wb") as f:
            f.write(response.content)
        mp3_paths.append(mp3_path)
        
        # Create permanent copy of chunk for individual access
        permanent_chunk = tempfile.NamedTemporaryFile(delete=False, suffix=f"_chunk_{idx}.mp3")
        with open(mp3_path, "rb") as src, open(permanent_chunk.name, "wb") as dst:
            dst.write(src.read())
        permanent_chunk_paths.append(permanent_chunk.name)
        
        print(f"[TTS] Completed chunk {idx}/{total}: {mp3_path}")
        print(f"[DEBUG] Permanent chunk created: {permanent_chunk.name}")
        if progress_callback:
            print(f"[DEBUG] Calling progress callback with {len(permanent_chunk_paths)} chunks")
            progress_callback(idx, total, permanent_chunk_paths)
    
    zip_path = os.path.join(temp_dir.name, "audio_chunks.zip")
    with zipfile.ZipFile(zip_path, "w") as zipf:
        for mp3_path in mp3_paths:
            arcname = os.path.basename(mp3_path)
            zipf.write(mp3_path, arcname=arcname)
    # Move zip to a permanent temp file
    zip_file = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with open(zip_path, "rb") as src, open(zip_file.name, "wb") as dst:
        dst.write(src.read())
    print(f"[TTS] All chunks completed. Zip created at: {zip_file.name}")
    return zip_file.name, permanent_chunk_paths


def generate_single_openai_tts(
    text, model, voice, speed, instructions, progress_callback=None
):
    print(f"[TTS] Generating single audio file for input text.")
    response = openai.audio.speech.create(
        model=model,
        voice=voice,
        input=text,
        speed=float(speed),
        response_format="mp3",
        instructions=instructions,
    )
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    temp.write(response.content)
    temp.close()
    print(f"[TTS] Single audio file created at: {temp.name}")
    if progress_callback:
        progress_callback(1, 1)
    return temp.name


def background_generate_audio(
    progress_id, text, model, voice, speed, instructions, is_file, audio_progress_data
):
    """
    Background function to generate audio with progress tracking.
    
    Args:
        progress_id: Unique identifier for tracking progress
        text: Text content to convert to audio
        model: OpenAI TTS model to use
        voice: Voice to use for TTS
        speed: Speech speed
        instructions: Additional instructions for TTS
        is_file: Boolean indicating if text comes from a file (affects output format)
        audio_progress_data: Shared dictionary for storing progress data
    """
    try:
        if is_file:
            # For file: zip of chunks
            def progress_callback(current, total, chunk_paths):
                print(f"[DEBUG] Progress callback called: current={current}, total={total}, chunks={len(chunk_paths)}")
                audio_progress_data[progress_id] = {
                    "current": current,
                    "total": total,
                    "status": "processing",
                    "chunks": [{"index": i+1, "path": path} for i, path in enumerate(chunk_paths)]
                }

            zip_path, chunk_paths = generate_openai_tts(
                text,
                model,
                voice,
                speed,
                instructions,
                progress_callback=progress_callback,
            )
            print(f"[DEBUG] Final chunk paths: {len(chunk_paths)} chunks")
            audio_progress_data[progress_id] = {
                "current": len(chunk_paths),
                "total": len(chunk_paths),
                "status": "done",
                "file_type": "zip",
                "file_path": zip_path,
                "chunks": [{"index": i+1, "path": path} for i, path in enumerate(chunk_paths)]
            }
        else:
            # For text: single mp3
            def progress_callback(current, total):
                audio_progress_data[progress_id] = {
                    "current": current,
                    "total": total,
                    "status": "processing",
                }

            mp3_path = generate_single_openai_tts(
                text,
                model,
                voice,
                speed,
                instructions,
                progress_callback=progress_callback,
            )
            audio_progress_data[progress_id] = {
                "current": 1,
                "total": 1,
                "status": "done",
                "file_type": "mp3",
                "file_path": mp3_path,
            }
    except Exception as e:
        audio_progress_data[progress_id] = {"status": "error", "error": str(e)}
