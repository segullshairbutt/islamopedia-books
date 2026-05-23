# Extract with Gemini Documentation

## Overview

`extract_with_gemini.py` extracts text from PDF files using Google Gemini Vision API. It converts each PDF page to a high-quality image (300 DPI JPEG) and uses Gemini's vision capabilities to extract text while preserving formatting, spacing, and structure. Each page is saved as a separate markdown file.

## Requirements

- Python 3.7+
- Google Gemini API key
- Dependencies:
  - `google-generativeai`
  - `pymupdf`
  - `python-dotenv`

All dependencies are specified in `pyproject.toml`.

## Setup

### 1. Install Dependencies

```bash
uv pip install
```

Or manually install:
```bash
pip install google-generativeai pymupdf python-dotenv
```

### 2. Configure Gemini API Key

You need a Google Gemini API key to use this script.

#### Option A: Using `.env` file (Recommended)

Create a `.env` file in the project root:

```bash
GEMINI_API_KEY=your_api_key_here
```

The script will automatically load this using `python-dotenv`.

#### Option B: Using Environment Variable

On macOS/Linux:
```bash
export GEMINI_API_KEY="your_api_key_here"
```

On Windows:
```bash
set GEMINI_API_KEY=your_api_key_here
```

#### Getting a Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the generated key
4. Add it to your `.env` file or environment variables

## Usage

### Basic Syntax

```bash
python extract_with_gemini.py <pdf_path> [--output-dir DIR] [--start-page NUM] [--end-page NUM]
```

### Arguments

- **pdf_path** (required): Path to the PDF file to extract
- **--output-dir** (optional): Directory to save markdown files. Default: `.pages`
- **--start-page** (optional): Starting page number (1-indexed). Default: First page
- **--end-page** (optional): Ending page number (1-indexed, inclusive). Default: Last page

## Usage Examples

### Extract All Pages (Default)

Extract all pages from a PDF and save to `.pages` directory:

```bash
python extract_with_gemini.py documents/book.pdf
```

Output:
```
Processing pages 1-653 (653 pages) from documents/book.pdf...
  Extracting page 1/653... ✓
  Extracting page 2/653... ✓
  ...
Extraction complete! 653 pages saved to .pages/
```

### Extract with Custom Output Directory

```bash
python extract_with_gemini.py documents/book.pdf --output-dir extracted_pages
```

### Extract Specific Page Range

Extract pages 50-100 from a PDF:

```bash
python extract_with_gemini.py documents/book.pdf --start-page 50 --end-page 100
```

Output:
```
Processing pages 50-100 (51 pages) from documents/book.pdf...
  Extracting page 50/100... ✓
  Extracting page 51/100... ✓
  ...
Extraction complete! 51 pages saved to .pages/
```

### Extract First N Pages

Extract only the first 20 pages:

```bash
python extract_with_gemini.py documents/book.pdf --end-page 20
```

### Extract from Specific Page to End

Extract from page 600 to the end:

```bash
python extract_with_gemini.py documents/book.pdf --start-page 600
```

### Extract with Custom Directory (Full Example)

```bash
python extract_with_gemini.py /path/to/large_document.pdf \
  --output-dir my_extracted_chapters \
  --start-page 100 \
  --end-page 250
```

## Output Format

### Directory Structure

```
.pages/
├── 01.md
├── 02.md
├── 03.md
├── ...
└── 653.md
```

### File Format

Each markdown file contains:

```markdown
# Page 1

[Extracted text with preserved formatting]

Lists are formatted with markdown syntax:
- Item 1
- Item 2

**Bold text** and *italic text* are preserved.
```

## Common Use Cases

### Workflow: Extract → Merge into Chapters

1. **Extract all pages** from a PDF:
   ```bash
   python extract_with_gemini.py books/my_book.pdf --output-dir .pages
   ```

2. **Merge pages** into chapters using the config file:
   ```bash
   python merge_pages.py .config/books_config.json
   ```

### Processing Large PDFs

For large PDFs, process in batches to manage API costs and errors:

```bash
# Extract pages 1-100
python extract_with_gemini.py document.pdf --end-page 100 --output-dir batch_1

# Extract pages 101-200
python extract_with_gemini.py document.pdf --start-page 101 --end-page 200 --output-dir batch_2

# Extract pages 201-end
python extract_with_gemini.py document.pdf --start-page 201 --output-dir batch_3
```

## Error Handling

### Common Errors

**ERROR: GEMINI_API_KEY not found in environment variables**

- Make sure `.env` file exists with `GEMINI_API_KEY=your_key_here`
- Or set the environment variable before running the script

**ERROR: PDF not found**

- Verify the PDF file path exists
- Use absolute path for clarity: `/full/path/to/file.pdf`

**ERROR: Start page must be before end page**

- Ensure `--start-page` is less than `--end-page`
- Example: `--start-page 10 --end-page 50` ✓

**ERROR: Page number out of range**

- Check the total number of pages in your PDF
- Example: If PDF has 653 pages, `--end-page 700` will fail

### Handling Failed Extractions

If individual pages fail during extraction:
- Failed pages are skipped with an error message
- Extraction continues with remaining pages
- A summary shows how many pages were successfully extracted

## Performance Notes

- Each page is processed sequentially
- API calls are made for each page (cost consideration)
- Image quality is set to 300 DPI for better OCR accuracy
- Processing time depends on PDF complexity and API response time

## Tips

- Test with a small page range first (e.g., `--start-page 1 --end-page 5`)
- Use custom output directories to organize different batches
- Monitor API usage and costs on your Gemini API dashboard
- The script preserves original formatting and markdown structure from PDFs
