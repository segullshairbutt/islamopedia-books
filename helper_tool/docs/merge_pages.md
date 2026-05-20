# Merge Pages Documentation

## Overview

`merge_pages.py` merges extracted page markdown files into chapter files based on a JSON configuration. It combines pages according to specified page ranges and reports missing pages inline.

## Requirements

- Python 3.7+
- Page markdown files in a directory (named as `01.md`, `02.md`, etc.)
- A configuration JSON file with chapter definitions

## Configuration Structure

The configuration file (`books_config.json`) defines input/output directories and chapter page ranges.

### Minimal JSON Structure

```json
{
    "inputDirectory": "/path/to/extracted/pages",
    "outputDirectory": "/path/to/output/chapters",
    "chapters": [
        {
            "name": "chapter_1.md",
            "startPage": 1,
            "endPage": 50
        },
        {
            "name": "chapter_2.md",
            "startPage": 51,
            "endPage": 100
        }
    ]
}
```

### Configuration Fields

- **inputDirectory** (required): Directory containing extracted page files (e.g., `01.md`, `02.md`, etc.)
- **outputDirectory** (required): Directory where merged chapter files will be saved
- **chapters** (required): Array of chapter objects
  - **name**: Output filename for the chapter
  - **startPage**: Starting page number (inclusive)
  - **endPage**: Ending page number (inclusive)

## Usage

```bash
python merge_pages.py /path/to/books_config.json
```

## Output

For each chapter defined in the config:
- Creates a merged markdown file with all pages in the specified range
- Pages are separated by `---` dividers
- Missing pages are marked inline with: `> ⚠️ Page X is missing here`
- Console output shows which pages were merged and which are missing

### Example Output File

```markdown
[Page 1 content]

---

[Page 2 content]

---

> ⚠️ Page 3 is missing here

---

[Page 4 content]
```

## Console Output Example

```
Processing: chapter_1.md
  Page range: 1-50
  Merged: 48 pages ⚠ Missing pages: 15, 32
  Output: /path/to/output/chapters/chapter_1.md

Processing: chapter_2.md
  Page range: 51-100
  Merged: 50 pages ✓
  Output: /path/to/output/chapters/chapter_2.md

============================================================
Summary: Merged 98 pages across 2 chapters
Warning: 2 pages were missing in the specified ranges
Output directory: /path/to/output/chapters
```

## Error Handling

- Config file must exist and be valid JSON
- Input directory must exist
- Output directory is created automatically if missing
- Missing page files are handled gracefully with inline warnings
