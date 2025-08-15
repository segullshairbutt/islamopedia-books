import io
import os
import tempfile
import zipfile

import pymupdf
from dotenv import load_dotenv
from google.cloud import vision

# Load environment variables from .env file
load_dotenv()

# Set Google Cloud credentials from environment variable if provided
google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
if google_credentials_path:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path


def detect_text(image_path):
    """
    Detects text in an image using Google Vision API.
    Args:
        image_path (str): The path to the image file.
    Returns:
        str: The detected text.
    """
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, "rb") as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    if texts:
        return texts[0].description
    if response.error.message:
        raise Exception(
            f"{response.error.message}\n"
            "For more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors"
        )
    return ""


def pdf_to_images(pdf_path, image_folder):
    """
    Converts each page of the PDF into an image and saves it.
    Args:
        pdf_path (str): Path to the input PDF.
        image_folder (str): Folder to save output images.
    Returns:
        list: A list of paths to the saved image files.
    """
    pdf_document = pymupdf.open(pdf_path)
    saved_images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image_path = os.path.join(image_folder, f"page_{page_num + 1}.jpg")
        pix.save(image_path)
        saved_images.append(image_path)
    return saved_images


def extract_pdf_text(pdf_path, output_folder, images_folder):
    """
    Extracts text from each page of a PDF and saves each page's text as a .txt file.
    Args:
        pdf_path (str): Path to the input PDF.
        output_folder (str): Folder to save output .txt files.
        images_folder (str): Folder to save intermediate images.
    Returns:
        list: List of output .txt file paths.
    """
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(images_folder, exist_ok=True)
    image_paths = pdf_to_images(pdf_path, images_folder)
    txt_files = []
    for idx, img_path in enumerate(image_paths, start=1):
        text = detect_text(img_path)
        txt_filename = f"page_{idx}.txt"
        txt_path = os.path.join(output_folder, txt_filename)
        with open(txt_path, "w", encoding="utf-8") as f:
            f.write(text)
        txt_files.append(txt_path)
        print(f"Extracted text for page {idx}: {txt_path}")
    return txt_files


def extract_pdf_text_to_zipfile(pdf_file):
    """
    Takes a PDF file (file-like object or path), extracts text from each page using Google Vision,
    writes each page's text to a .txt file, zips them, and returns the zip file path.
    Args:
        pdf_file: file-like object (with .read()) or file path (str)
    Returns:
        str: Path to the generated zip file containing all .txt files.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save PDF to a temp file if it's a file-like object
        if hasattr(pdf_file, "read"):
            pdf_path = os.path.join(temp_dir, "input.pdf")
            with open(pdf_path, "wb") as f:
                f.write(pdf_file.read())
        else:
            pdf_path = pdf_file

        txt_folder = os.path.join(temp_dir, "txts")
        images_folder = os.path.join(temp_dir, "images")
        # Use the existing extract_pdf_text function to generate txt files
        txt_files = extract_pdf_text(pdf_path, txt_folder, images_folder)

        # Create a zip file of all txt files
        zip_path = os.path.join(temp_dir, "pages.zip")
        with zipfile.ZipFile(zip_path, "w") as zipf:
            for txt_file in txt_files:
                arcname = os.path.basename(txt_file)
                zipf.write(txt_file, arcname=arcname)

        # Move the zip file to a permanent temp file and return its path
        final_zip = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        with open(zip_path, "rb") as src, open(final_zip.name, "wb") as dst:
            dst.write(src.read())
        return final_zip.name


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract text from PDF using Google Vision API."
    )
    parser.add_argument("pdf_path", help="Path to the PDF file.")
    parser.add_argument(
        "--output_folder",
        default="output_txt",
        help="Folder to save .txt files.",
    )
    parser.add_argument(
        "--images_folder",
        default="output_images",
        help="Folder to save images.",
    )
    args = parser.parse_args()

    if not os.path.exists(args.pdf_path):
        print(f"PDF file not found: {args.pdf_path}")
    else:
        print("Extracting text from PDF...")
        extract_pdf_text(args.pdf_path, args.output_folder, args.images_folder)
