import os
import io
import fitz
from google.cloud import vision

def initialize_paths():
    """Initialize and create necessary directories and paths."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
    upload_folder = os.path.join(base_dir, "uploads")
    text_folder = os.path.join(base_dir, "extracted_text")
    images_folder = os.path.join(base_dir, "extracted_images")
    os.makedirs(images_folder, exist_ok=True)
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    return base_dir, upload_folder, text_folder, images_folder

def detect_text(path, output_file):

    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations
    print(f"Detected {len(texts)} text annotations.")

    if texts:
        full_text = texts[0].description
        with open(output_file, 'a', encoding='utf-8') as md_file:
            md_file.write(full_text)
            print(f"Appended text to output file.")

    if response.error.message:
        raise Exception(
            '{}\nFor more info on error messages, check: '
            'https://cloud.google.com/apis/design/errors'.format(
                response.error.message))

def pdf_to_images(pdf_path, image_folder, text_folder):
    pdf_document = fitz.open(pdf_path)
    saved_images = []
    page_ranges = [
        (2,8),(9, 60), (61, 88), (89, 97), (98, 161), (162, 166),
        (167, 177), (178, 255), (256, 326), (327, 337)
    ]
    output_files = [
        os.path.join(text_folder, f'range_{start}_{end}.md')
        for start, end in page_ranges
    ]

    for output_file in output_files:

        with open(output_file, 'w', encoding='utf-8') as md_file:
            md_file.write("")

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image_path = os.path.join(image_folder, f"page_{page_num+1}.jpg")
        pix.save(image_path)
        saved_images.append(image_path)
        print(f"Saved image: {image_path}")

        for (start, end), output_file in zip(page_ranges, output_files):
            if start <= page_num + 1 <= end:
                detect_text(image_path, output_file)
                break

    return saved_images

if __name__ == "__main__":
    base_dir, upload_folder, text_folder, images_folder = initialize_paths()
    pdf_file_path = os.path.join(upload_folder, "Tarikh Ibn e Kaseer 3.pdf")
    if not os.path.exists(pdf_file_path):
        print(f"PDF file not found: {pdf_file_path}")
    else:
        print(f"Converting PDF to images..")
        pdf_to_images(pdf_file_path, images_folder, text_folder)