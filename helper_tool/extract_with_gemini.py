#!/usr/bin/env python3
"""
Extract text from PDF using Google Gemini Vision API.
Saves each page as a separate markdown file.
"""

import argparse
import base64
import os
from pathlib import Path

import pymupdf
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Gemini
try:
    import google.generativeai as genai
except ImportError:
    print("ERROR: google-generativeai not installed. Install it with:")
    print("  pip install google-generativeai")
    exit(1)

# Configure Gemini API
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    print("ERROR: GEMINI_API_KEY not found in environment variables.")
    print("Add it to your .env file: GEMINI_API_KEY=your_key_here")
    exit(1)

genai.configure(api_key=api_key)


def pdf_page_to_image_bytes(pdf_path: str, page_num: int) -> bytes:
    """
    Converts a specific PDF page to image bytes (JPEG format).

    Args:
        pdf_path: Path to the input PDF
        page_num: Page number (0-indexed)

    Returns:
        bytes: JPEG image data
    """
    pdf_document = pymupdf.open(pdf_path)
    page = pdf_document.load_page(page_num)
    pix = page.get_pixmap(dpi=300)
    image_bytes = pix.tobytes("jpeg")
    pdf_document.close()
    return image_bytes


def extract_text_with_gemini(image_bytes: bytes) -> str:
    """
    Uses Gemini Vision to extract text from an image.

    Args:
        image_bytes: JPEG image data as bytes

    Returns:
        str: Extracted text
    """
    model = genai.GenerativeModel("gemini-2.5-flash-lite")

    # Encode image to base64
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")

    # Create the message with vision capabilities
    message = model.generate_content(
        [
            {
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "image/jpeg",
                            "data": image_data,
                        }
                    },
                    {
                        "text": "Extract all text from this image exactly as shown. Preserve the exact formatting, spacing, paragraphs, and structure. Use markdown format where appropriate (lists, emphasis, code blocks). Do NOT add any commentary, explanations, or extra information. Return ONLY the extracted text in markdown format, nothing more."
                    },
                ],
            }
        ]
    )

    return message.text


def extract_pdf_with_gemini(pdf_path: str, output_dir: str = ".pages") -> list:
    """
    Extracts text from all PDF pages using Gemini and saves as markdown files.

    Args:
        pdf_path: Path to the input PDF
        output_dir: Directory to save markdown files (default: .pages)

    Returns:
        list: List of created markdown file paths
    """
    # Validate PDF exists
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Get total pages
    pdf_document = pymupdf.open(pdf_path)
    total_pages = len(pdf_document)
    pdf_document.close()

    print(f"Processing {total_pages} pages from {pdf_path}...")

    created_files = []

    for page_num in range(total_pages):
        print(f"  Extracting page {page_num + 1}/{total_pages}...", end=" ", flush=True)

        try:
            # Convert page to image
            image_bytes = pdf_page_to_image_bytes(pdf_path, page_num)

            # Extract text with Gemini
            extracted_text = extract_text_with_gemini(image_bytes)

            # Save as markdown
            md_filename = f"{page_num + 1:02d}.md"
            md_path = output_path / md_filename

            with open(md_path, "w", encoding="utf-8") as f:
                f.write(f"# Page {page_num + 1}\n\n")
                f.write(extracted_text)

            created_files.append(str(md_path))
            print("✓")

        except Exception as e:
            print(f"✗ Error: {e}")
            continue

    print(f"\nExtraction complete! {len(created_files)} pages saved to {output_dir}/")
    return created_files


def main():
    parser = argparse.ArgumentParser(description="Extract text from PDF using Google Gemini Vision API.")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output-dir", default=".pages", help="Output directory for markdown files (default: .pages)")

    args = parser.parse_args()

    try:
        extract_pdf_with_gemini(args.pdf_path, args.output_dir)
    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)


if __name__ == "__main__":
    main()
