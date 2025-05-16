import os
import io
import fitz
from google.cloud import vision

def detect_text(path, output_file):
    """
    Detects text in an image and appends it to the output file.
    Args:
        path (str): The path to the image file.
        output_file (str): The path to the output text file.
    """
    client = vision.ImageAnnotatorClient()
    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    texts = response.text_annotations
    print(f"Detected {len(texts)} text annotations in {os.path.basename(path)}.")
    if texts:
        full_text = texts[0].description
        with open(output_file, 'a', encoding='utf-8') as md_file:
            md_file.write(full_text)
            print(f"Appended text to {output_file}.")
    if response.error.message:
        raise Exception(
            f"{response.error.message}\n"
            "For more info on error messages, check: "
            "https://cloud.google.com/apis/design/errors"
        )
        
def pdf_to_images(pdf_path, image_folder):
    """
    Converts each page of the PDF into an image and saves it.
    Args:
        pdf_path (str): Path to the input PDF.
        image_folder (str): Folder to save output images.

    Returns:
        list: A list of paths to the saved image files.
    """
    pdf_document = fitz.open(pdf_path)
    saved_images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image_path = os.path.join(image_folder, f"page_{page_num+1}.jpg")
        pix.save(image_path)
        saved_images.append(image_path)
        print(f"Saved image: {image_path}")
    return saved_images

def process_images_for_text(image_paths, text_files_folder):
    """
    Processes a list of image paths and extracts text to files based on defined page ranges.
    Args:
        image_paths (list): List of image paths.
        text_files_folder (str): Folder to store the output text files.
    """
    page_ranges = [
        (2, 3),
    ]
    output_files = [
        os.path.join(text_files_folder, f'range_{start}_{end}.md')
        for start, end in page_ranges
    ]
    for img_path in image_paths:
        page_num = int(os.path.basename(img_path).split("_")[1].split(".")[0])
        for (start, end), output_file in zip(page_ranges, output_files):
            if start <= page_num <= end:
                detect_text(img_path, output_file)
                break
            
if __name__ == "__main__":
    upload_folder = os.getenv("UPLOAD_FOLDER")
    text_files_folder = os.getenv("TEXT_FILES_FOLDER")
    images_folder = os.getenv("IMAGES_FOLDER")

    os.makedirs(images_folder, exist_ok=True)
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    pdf_filename = os.getenv("PDF_FILENAME", "Tarikh Ibn e Kaseer 3.pdf")
    pdf_file_path = os.path.join(upload_folder, pdf_filename)
    if not os.path.exists(pdf_file_path):
        print(f"PDF file not found: {pdf_file_path}")
    else:
        print("Converting PDF to images...")
        images = pdf_to_images(pdf_file_path, images_folder)
        print("Extracting text from images...")
        process_images_for_text(images, text_files_folder)
