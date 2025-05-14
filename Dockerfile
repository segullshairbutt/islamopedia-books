# Use an official Python runtime as a parent image
FROM python:3.12.7-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Install Poetry
RUN pip install poetry==2.0.0

# Copy the poetry.lock and pyproject.toml files
COPY pyproject.toml poetry.lock /app/

# Do not create a virtualenv
RUN poetry config virtualenvs.create false

# Install the dependencies
RUN poetry install

# Copy the rest of the application code to the container
COPY . /app/

# Set environment variables for Google Cloud credentials and other paths
ENV GOOGLE_APPLICATION_CREDENTIALS="segulshairbutt-google-fusion-ai.json"
ENV UPLOAD_FOLDER="/app/uploads"
ENV TEXT_FOLDER="/app/extracted_text"
ENV IMAGES_FOLDER="/app/extracted_images"
ENV PDF_FILENAME="Tarikh Ibn e Kaseer 3.pdf"

# Co
