FROM python:3.12.7-slim-bullseye

WORKDIR /app

# Install system dependencies required by PyMuPDF/fitz
RUN apt-get update && apt-get install -y libglib2.0-0 libxrender1 libsm6 libxext6 && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY scripts/text_extractor_from_images/requirments.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirments.txt

# Prepare necessary folders
RUN mkdir -p uploads text_files images

# Copy your project files into the container
COPY . .

CMD ["python3", "scripts/text_extractor_from_images/pdf_text_extractor.py"]
