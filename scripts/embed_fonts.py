#!/usr/bin/env python3
"""Generate a self-contained ``base.css`` for a Jupyter Book 2 (MyST) book.

MyST only bundles the single stylesheet referenced by ``site.options.style`` in
``myst.yml``; it does **not** follow ``@import`` statements or copy the font
files referenced by ``url(...)``. So the fonts have to be inlined.

This script reads the editable source ``_static/base.src.css``, inlines any
``@import`` it contains, and rewrites every ``url("./relative")`` reference to a
base64 ``data:`` URI. The result is written to ``_static/base.css`` (the file
MyST actually loads).

Usage:
    python scripts/embed_fonts.py books/template_book
    # or, for every book:
    for d in books/*/; do python scripts/embed_fonts.py "$d"; done
"""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

# file extension -> CSS font MIME type
MIME = {
    ".woff2": "font/woff2",
    ".woff": "font/woff",
    ".ttf": "font/ttf",
    ".otf": "font/otf",
}

URL_RE = re.compile(r'url\(\s*["\']?(?!data:)([^"\')]+)["\']?\s*\)')
IMPORT_RE = re.compile(r'@import\s+url\(\s*["\']?([^"\')]+)["\']?\s*\)\s*;')


def to_data_uri(path: Path) -> str:
    mime = MIME.get(path.suffix.lower(), "application/octet-stream")
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def inline_urls(css: str, base_dir: Path) -> str:
    """Rewrite every url(./x) in ``css`` (resolved against ``base_dir``) to a data URI."""

    def repl(match: re.Match) -> str:
        ref = match.group(1).strip()
        if ref.startswith(("http://", "https://", "//")):
            return match.group(0)
        target = (base_dir / ref).resolve()
        if not target.exists():
            raise FileNotFoundError(f"referenced asset not found: {target}")
        return f'url("{to_data_uri(target)}")'

    return URL_RE.sub(repl, css)


def expand(css: str, base_dir: Path) -> str:
    """Inline @import files, then inline url() font references."""

    def repl_import(match: re.Match) -> str:
        ref = match.group(1).strip()
        imported = (base_dir / ref).resolve()
        text = imported.read_text(encoding="utf-8")
        # url()s inside the imported file are relative to *its* directory
        return inline_urls(text, imported.parent)

    css = IMPORT_RE.sub(repl_import, css)
    return inline_urls(css, base_dir)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    book = Path(argv[1]).resolve()
    static = book / "_static"
    src = static / "base.src.css"
    out = static / "base.css"
    if not src.exists():
        print(f"error: {src} not found", file=sys.stderr)
        return 1
    result = expand(src.read_text(encoding="utf-8"), static)
    out.write_text(result, encoding="utf-8")
    size_mb = out.stat().st_size / 1024 / 1024
    print(f"wrote {out} ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
