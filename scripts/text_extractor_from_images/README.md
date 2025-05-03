# PDF to OCR Text Extractor – Code Summary

## 📄 Purpose
Extracts text from a PDF using Google Cloud Vision OCR, based on predefined page ranges, and saves the text into Markdown files.

---

## 🗂 Folder Setup
- **UPLOAD_FOLDER**: Location of the PDF file.
- **TEXT_FOLDER**: Where extracted text (Markdown files) is saved.
- **IMAGES_FOLDER**: Where PDF pages are saved as images.
- Creates the folders if they don't exist.

---

## 🔐 Authentication
Sets Google Cloud credentials using the environment variable `GOOGLE_APPLICATION_CREDENTIALS`.

---

## 🔍 Function: `detect_text(path, output_file)`
- Reads an image file.
- Sends it to **Google Cloud Vision** for text detection.
- Appends the detected text to the specified `.md` file.
- Logs the number of annotations and handles API errors.

---

## 🖼️ Function: `pdf_to_images(pdf_path, image_folder)`
- Opens the PDF using `PyMuPDF (fitz)`.
- Defines specific page ranges and corresponding Markdown output files.
- Clears any existing content in output files.
- Converts each page into a 300 DPI image.
- Saves images to disk.
- Determines which page range the image belongs to.
- Calls `detect_text()` to process and store text.

---

## 🏃 Main Execution
- Sets the PDF file path.
- Verifies file existence.
- Calls `pdf_to_images()` to start processing.

---

## ✅ Output
- Extracted text organized into Markdown files by page ranges.
- Images of PDF pages saved for reference or reuse.