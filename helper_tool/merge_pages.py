#!/usr/bin/env python3
"""
Merge extracted pages into chapter files based on configuration.
Combines page markdown files according to startPage and endPage ranges.
Reports missing pages in the specified ranges.
"""

import argparse
import json
import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Chapter:
    """Represents a single chapter configuration."""

    name: str
    start_page: int
    end_page: int

    def __repr__(self) -> str:
        return f"Chapter(name={self.name}, pages={self.start_page}-{self.end_page})"


@dataclass
class BooksConfig:
    """Represents the overall books configuration."""

    input_directory: str
    output_directory: str
    chapters: list[Chapter]

    @classmethod
    def from_json(cls, config_path: str) -> "BooksConfig":
        """
        Load configuration from a JSON file.

        Args:
            config_path: Path to the JSON config file

        Returns:
            BooksConfig: Parsed configuration object

        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
            KeyError: If required fields are missing
        """
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Validate required fields
        required_fields = ["inputDirectory", "outputDirectory", "chapters"]
        for field in required_fields:
            if field not in data:
                raise KeyError(f"Missing required field in config: {field}")

        # Parse chapters
        chapters = [
            Chapter(
                name=ch["name"],
                start_page=ch["startPage"],
                end_page=ch["endPage"],
            )
            for ch in data["chapters"]
        ]

        return cls(
            input_directory=data["inputDirectory"],
            output_directory=data["outputDirectory"],
            chapters=chapters,
        )

    def __repr__(self) -> str:
        return (
            f"BooksConfig(input={self.input_directory}, output={self.output_directory}, chapters={len(self.chapters)})"
        )


def check_missing_pages(input_dir: str, start_page: int, end_page: int) -> tuple[list[int], list[int]]:
    """
    Check which pages exist and which are missing in a range.

    Args:
        input_dir: Directory containing page files
        start_page: Starting page number (inclusive)
        end_page: Ending page number (inclusive)

    Returns:
        tuple: (existing_pages, missing_pages) - sorted lists of page numbers
    """
    existing_pages = []
    missing_pages = []

    for page_num in range(start_page, end_page + 1):
        page_file = Path(input_dir) / f"{page_num:02d}.md"
        if page_file.exists():
            existing_pages.append(page_num)
        else:
            missing_pages.append(page_num)

    return existing_pages, missing_pages


def merge_pages(input_dir: str, output_path: str, start_page: int, end_page: int) -> tuple[int, list[int]]:
    """
    Merge pages within a range into a single file.

    Args:
        input_dir: Directory containing page markdown files
        output_path: Path to write merged output file
        start_page: Starting page number (inclusive)
        end_page: Ending page number (inclusive)

    Returns:
        tuple: (pages_merged, missing_pages) - count of merged pages and list of missing page numbers
    """
    existing_pages, missing_pages = check_missing_pages(input_dir, start_page, end_page)

    # Create output directory if needed
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Merge existing pages
    merged_content = []

    # Process pages in sequence, adding inline notes for missing pages
    for page_num in range(start_page, end_page + 1):
        page_file = Path(input_dir) / f"{page_num:02d}.md"

        if page_file.exists():
            with open(page_file, "r", encoding="utf-8") as f:
                content = f.read()
                merged_content.append(content)
                merged_content.append("\n\n---\n\n")  # Page separator
        else:
            # Add inline note for missing page
            merged_content.append(f"> ⚠️ Page {page_num} is missing here\n\n")
            merged_content.append("---\n\n")

    # Remove trailing separator
    if merged_content:
        merged_content.pop()

    # Write merged content
    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(merged_content)

    return len(existing_pages), missing_pages


def process_chapters(config: BooksConfig) -> None:
    """
    Process all chapters: merge pages and report missing pages.

    Args:
        config: BooksConfig object with chapter definitions
    """
    # Validate input directory
    if not os.path.exists(config.input_directory):
        raise FileNotFoundError(f"Input directory not found: {config.input_directory}")

    print(f"Processing {len(config.chapters)} chapters...\n")

    total_merged = 0
    total_missing = 0

    for chapter in config.chapters:
        output_path = os.path.join(config.output_directory, chapter.name)

        print(f"Processing: {chapter.name}")
        print(f"  Page range: {chapter.start_page}-{chapter.end_page}")

        pages_merged, missing_pages = merge_pages(
            config.input_directory,
            output_path,
            chapter.start_page,
            chapter.end_page,
        )

        total_merged += pages_merged
        total_missing += len(missing_pages)

        print(f"  Merged: {pages_merged} pages", end="")

        if missing_pages:
            missing_str = ", ".join(str(p) for p in missing_pages)
            print(f" ⚠ Missing pages: {missing_str}")
        else:
            print(" ✓")

        print(f"  Output: {output_path}\n")

    # Summary
    print("=" * 60)
    print(f"Summary: Merged {total_merged} pages across {len(config.chapters)} chapters")
    if total_missing > 0:
        print(f"Warning: {total_missing} pages were missing in the specified ranges")
    print(f"Output directory: {config.output_directory}")


def main():
    parser = argparse.ArgumentParser(description="Merge extracted pages into chapters based on configuration.")
    parser.add_argument(
        "config_path",
        help="Path to the books_config.json configuration file",
    )

    args = parser.parse_args()

    try:
        # Load configuration
        config = BooksConfig.from_json(args.config_path)
        print(f"Loaded configuration: {config}\n")

        # Process chapters
        process_chapters(config)

    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)


if __name__ == "__main__":
    main()
