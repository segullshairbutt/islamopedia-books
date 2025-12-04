# Helper Tool

A minimal Flask application with two endpoints: `/extract-text` and `/generate-audio`.

## Setup and Run

This project uses `uv` for package management and `pyproject.toml` for dependencies.

1.  **Install `uv`:**

    If you don't have `uv` installed, follow the instructions on the [official `uv` website](https://github.com/astral-sh/uv).

2.  **Create a virtual environment:**

    ```bash
    uv venv
    ```

3.  **Activate the virtual environment:**

    -   On macOS and Linux:
        ```bash
        source .venv/bin/activate
        ```
    -   On Windows:
        ```bash
        .venv\Scripts\activate
        ```

4.  **Install dependencies from `pyproject.toml`:**

    ```bash
    uv pip install
    ```

5.  **Set up Google Cloud Vision credentials:**

    The `/extract-text` endpoint uses the Google Cloud Vision API.  
    You must set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to the path of your Google service account JSON key file:

    - On macOS and Linux:
        ```bash
        export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-key.json"
        ```
    - On Windows:
        ```bash
        set GOOGLE_APPLICATION_CREDENTIALS="C:\path\to\your\service-account-key.json"
        ```

6.  **Run the application:**

    ```bash
    flask run
    ```
    Or
    ```bash
    python app.py
    ```

    The application will be running at `http://127.0.0.1:5000`.

## Endpoints

-   `GET /extract-text`: Upload a PDF and download a zip of per-page text files extracted using Google Vision.
-   `POST /extract-text`: Accepts a PDF file upload and returns a zip file of extracted text.
-   `GET /generate-audio`: Page for audio generation (work in progress).
-   `POST /generate-audio`: Endpoint for audio generation (work in progress).

**Note:**  
The `/extract-text` endpoint requires a valid Google Cloud Vision API key and the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to be set.
