import os
import fitz

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
IMAGES_FOLDER = os.path.join(BASE_DIR, "books/template_book/images")

os.makedirs(IMAGES_FOLDER, exist_ok=True)

print(f"Upload folder: {UPLOAD_FOLDER}")
print(f"Images folder: {IMAGES_FOLDER}")

def pdf_to_images(pdf_path, image_folder):
    pdf_document = fitz.open(pdf_path)
    saved_images = []
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image_path = os.path.join(image_folder, f"page_{page_num+1}.png")
        pix.save(image_path)
        saved_images.append(image_path)
        print(f"Saved image: {image_path}")
    return saved_images

if __name__ == "__main__":
    pdf_file_path = os.path.join(UPLOAD_FOLDER, "first_check_file.pdf")
    if not os.path.exists(pdf_file_path):
        print(f"PDF file not found: {pdf_file_path}")
    else:
        print(f"Converting PDF to images: {pdf_file_path}")
        pdf_to_images(pdf_file_path, IMAGES_FOLDER)
