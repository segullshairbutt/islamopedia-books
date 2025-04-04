import os
import fitz  # PyMuPDF
from PIL import Image
import openai
import pytesseract
import re

# Clean non-Urdu lines
def clean_english_gibberish(text):
    urdu_lines = [line for line in text.splitlines() if re.search(r'[\u0600-\u06FF]', line)]
    return "\n".join(urdu_lines)

# OpenAI API setup
client = openai.OpenAI(os.environ.get("OPENAI_API_KEY"))

# Define base directories
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
OUTPUT_FOLDER = os.path.join(BASE_DIR, "books/template_book/uploaded_content")
IMAGES_FOLDER = os.path.join(BASE_DIR, "books/template_book/images")

# Ensure folders exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)

print(f"Upload folder: {UPLOAD_FOLDER}")
print(f"Output folder: {OUTPUT_FOLDER}")
print(f"Images folder: {IMAGES_FOLDER}")

# Convert PDF pages to images and save them
def pdf_to_images(pdf_path, image_folder):
    pdf_document = fitz.open(pdf_path)
    saved_images = []

    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap(dpi=300)
        image_path = os.path.join(UPLOAD_FOLDER, f"page_{page_num+1}.png")
        pix.save(image_path)
        saved_images.append(image_path)
        print(f"Saved image: {image_path}")

    return saved_images

# Send text to ChatGPT for proofreading
def proofread_text_with_chatgpt(text):
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "آپ ایک اردو پروف ریڈر ہیں۔ درج ذیل اردو متن میں املا، گرامر اور جملوں کی ساخت کو درست کریں۔"},
                {"role": "user", "content": text}
            ],
            temperature=0.2,
            max_tokens=2048,
            stream=False
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error during ChatGPT proofreading: {e}")
        return text

# Save plain text
def save_text_as_txt(text, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

# Extract Urdu text from images and proofread
def process_images_for_proofreading(image_folder):
    for img_name in os.listdir(image_folder):
        if img_name.lower().endswith((".png", ".jpg", ".jpeg")):
            img_path = os.path.join(image_folder, img_name)
            print(f"Processing image: {img_path}")

            # Load image
            img = Image.open(img_path)

            # OCR
            text = pytesseract.image_to_string(img, lang="urd+eng", config="--psm 4")
            cleaned_text = clean_english_gibberish(text)

            # Proofread
            proofread = proofread_text_with_chatgpt(cleaned_text)

            # Save proofread text
            output_txt = os.path.splitext(img_path)[0] + ".txt"
            save_text_as_txt(proofread, output_txt)
            print(f"Proofread text saved: {output_txt}")

# Example usage
if __name__ == "__main__":
    pdf_file_path = os.path.join(UPLOAD_FOLDER, "myAssignment.pdf")
    if not os.path.exists(pdf_file_path):
        print(f"PDF file not found: {pdf_file_path}")
    else:
        print(f"Converting PDF to images: {pdf_file_path}")
        image_files = pdf_to_images(pdf_file_path, IMAGES_FOLDER)
        process_images_for_proofreading(IMAGES_FOLDER)
