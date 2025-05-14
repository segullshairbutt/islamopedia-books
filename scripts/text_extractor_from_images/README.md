## How to Run the PDF Extractor

1. **Install Dependencies**:
   Ensure you have Python installed and install required libraries using:

   ```bash
   pip install -r requirements.txt
   OR
   you can manully install the required libraries by running the following commands:
   pip install PyPDF2
   pip install google-cloud-vision
   ```

2. **Set Google Cloud Credentials**:
   Export your Google Cloud Vision API credentials:

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
   ```

   After setting the environment variable, the credentials can be accessed in the `pdf_text_extractor.py` file.
   you can mention the file path manully in your envoironment variable like this GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
   and after that you can access it in pdf_text_extractor.py file.

   ```

   ```

3. **Prepare Folders**:
   Create the necessary folders (`UPLOAD_FOLDER`, `TEXT_FOLDER`, `IMAGES_FOLDER`) or ensure they exist.
   UPLOAD_FOLDER:

    This folder is likely used to store the uploaded PDF files temporarily before processing.
    It acts as a staging area for input files.
    TEXT_FOLDER:

    This folder is used to store the extracted text from the PDF files.
    Each processed PDF might generate a corresponding text file saved here.
    IMAGES_FOLDER:

    This folder is used to store images extracted from the PDF pages.
    If the script processes PDFs to extract images (e.g., for OCR or other purposes), those images will be saved here.

4. **Run the Script**:
   Execute the script with the following command:

   ```bash
   python pdf_extractor.py --pdf <path_to_pdf> --ranges <page_ranges>
   ```

   Replace `<path_to_pdf>` with the path to your PDF file and `<page_ranges>` with the desired page ranges (e.g., `1-5,7-10`).

5. **Check Output**:
   - Extracted text will be saved in the `TEXT_FOLDER`.
   - Images of PDF pages will be saved in the `IMAGES_FOLDER`.
