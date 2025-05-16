## How to Run the PDF Extractor

1. **Install Dependencies**:
   Ensure you have Python installed and install required libraries using:

   ```bash
   pip install -r requirements.txt
   OR
   #you can manully install the required libraries by running the following commands:
   pip install PyPDF2
   pip install google-cloud-vision
   ```

2. **Set Google Cloud Credentials**:
   Export your Google Cloud Vision API credentials:

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"
   ```

   After setting the environment variable, the credentials can be accessed in the `pdf_text_extractor.py` file.
   you can mention the file path manully in your envoironment variable like this `GOOGLE_APPLICATION_CREDENTIALS="path/to/your/credentials.json"`
   and after that you can access it in `pdf_text_extractor.py` file.

3. **Prepare Folders**:
   Create the necessary folders (`UPLOAD_FOLDER`, `TEXT_FILES_FOLDER`, `IMAGES_FOLDER`) or ensure they exist.
   **UPLOAD_FOLDER:**

    This folder is likely used to store the uploaded PDF files temporarily before processing.
    It acts as a staging area for input files.
    **TEXT_FOLDER:**

    This folder is used to store the extracted text from the PDF files.
    Each processed PDF might generate a corresponding text file saved here.
    **IMAGES_FOLDER:**

    This folder is used to store images extracted from the PDF pages.
    If the script processes PDFs to extract images (e.g., for OCR or other purposes), those images will be saved here.

4. **Run the Script**:
   Execute the script with the following command:

   ```bash
   python3 scripts/text_extractor_from_images/pdf_text_extractor.py
   ```
   Make sure you have added the `pdf_file` to uploads folder(locating in main directory) before running the script.

   **Using Docker Image**:
   You can also run the script using Docker. First, build the Docker image:
   ```bash
   docker build -t pdf-text-extractor .
   #Then, run the container:
   docker run --rm \ --name my_pdf_extractor \ -e GOOGLE_APPLICATION_CREDENTIALS="/app/credentials.json" \ -v $(pwd):/app \ pdf-text-extractor
   ```

5. **Check Output**:
   - Extracted text will be saved in the `TEXT_FOLDER`.
   - Images of PDF pages will be saved in the `IMAGES_FOLDER`.
