#!/usr/bin/env python3
"""
Merge extracted markdown pages into chapter files based on configuration.
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

    input_directory: Path
    output_directory: Path
    chapters: list[Chapter]

    @classmethod
    def from_json(cls, config_path: str) -> "BooksConfig":
        """
        Load configuration from a JSON file.
        Resolves relative paths relative to the config file's directory.
        """
        config_file = Path(config_path).resolve()
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")

        with open(config_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Support both camelCase and snake_case
        input_dir_str = data.get("inputDirectory") or data.get("input_directory")
        output_dir_str = data.get("outputDirectory") or data.get("output_directory")
        chapters_data = data.get("chapters")

        if not input_dir_str:
            raise KeyError("Missing required field in config: inputDirectory (or input_directory)")
        if not output_dir_str:
            raise KeyError("Missing required field in config: outputDirectory (or output_directory)")
        if chapters_data is None:
            raise KeyError("Missing required field in config: chapters")

        # Resolve paths (relative to config file directory if not absolute)
        config_dir = config_file.parent
        input_path = Path(input_dir_str)
        if not input_path.is_absolute():
            input_path = (config_dir / input_path).resolve()

        output_path = Path(output_dir_str)
        if not output_path.is_absolute():
            output_path = (config_dir / output_path).resolve()

        # Parse chapters
        chapters = []
        for ch in chapters_data:
            name = ch.get("name") or ch.get("output_file")
            start_page = ch.get("startPage") if "startPage" in ch else ch.get("start_page")
            end_page = ch.get("endPage") if "endPage" in ch else ch.get("end_page")

            if not name or start_page is None or end_page is None:
                raise ValueError(f"Each chapter must have 'name', 'startPage', and 'endPage': {ch}")

            chapters.append(
                Chapter(
                    name=str(name),
                    start_page=int(start_page),
                    end_page=int(end_page),
                )
            )

        return cls(
            input_directory=input_path,
            output_directory=output_path,
            chapters=chapters,
        )


def find_page_file(input_dir: Path, page_num: int) -> Path | None:
    """
    Find the page markdown file matching common naming conventions:
    - 01.md, 1.md, 001.md, 0001.md, page_1.md, page_01.md
    """
    candidates = [
        input_dir / f"{page_num:02d}.md",
        input_dir / f"{page_num}.md",
        input_dir / f"{page_num:03d}.md",
        input_dir / f"{page_num:04d}.md",
        input_dir / f"page_{page_num}.md",
        input_dir / f"page_{page_num:02d}.md",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def merge_pages(input_dir: Path, output_file: Path, start_page: int, end_page: int) -> tuple[int, list[int]]:
    """
    Merge pages within a range into a single markdown file.

    Args:
        input_dir: Directory containing page markdown files
        output_file: Path to write the merged chapter file
        start_page: Starting page number (inclusive)
        end_page: Ending page number (inclusive)

    Returns:
        tuple: (pages_merged, missing_pages)
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    merged_content = []
    existing_pages = []
    missing_pages = []

    for page_num in range(start_page, end_page + 1):
        page_file = find_page_file(input_dir, page_num)

        if page_file is not None:
            with open(page_file, "r", encoding="utf-8") as f:
                content = f.read()
                merged_content.append(content)
                merged_content.append("\n\n---\n\n")  # Page separator
            existing_pages.append(page_num)
        else:
            merged_content.append(f"> ⚠️ Page {page_num} is missing here\n\n")
            merged_content.append("---\n\n")
            missing_pages.append(page_num)

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
    """
    if not config.input_directory.exists():
        raise FileNotFoundError(f"Input directory not found: {config.input_directory}")

    print(f"Processing {len(config.chapters)} chapters...\n")

    total_merged = 0
    total_missing = 0

    for chapter in config.chapters:
        output_path = config.output_directory / chapter.name

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
    parser = argparse.ArgumentParser(description="Merge extracted markdown pages into chapters based on configuration.")
    parser.add_argument(
        "config_path",
        help="Path to the books_config.json configuration file",
    )

    args = parser.parse_args()

    try:
        config = BooksConfig.from_json(args.config_path)
        print(f"Loaded configuration from: {args.config_path}")
        print(f"  Input Directory:  {config.input_directory}")
        print(f"  Output Directory: {config.output_directory}")
        print(f"  Chapters to process: {len(config.chapters)}\n")

        process_chapters(config)

    except Exception as e:
        print(f"ERROR: {e}")
        exit(1)


if __name__ == "__main__":
    main()
