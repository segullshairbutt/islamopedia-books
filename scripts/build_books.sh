#!/bin/bash
# Build every book into the Firebase `static/` public directory, using the
# Docker builder image (which bundles Python, uv and the Node.js runtime that
# MyST needs). All books are expected to be Jupyter Book 2 (MyST) projects.
#
# Each book is hosted at `/<book_name>/`, so it is built with
# BASE_URL=/<book_name> to make the theme's absolute asset paths resolve there.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

IMAGE="islamopedia-books-builder"
STATIC="$ROOT/static"

echo "Building Docker image '$IMAGE' ..."
docker build -t "$IMAGE" .

built=0
for dir in "$ROOT"/books/*/; do
    book="$(basename "$dir")"

    echo "Building '$book' (baseurl /$book) ..."
    # Generate the self-contained _static/base.css (fonts inlined) inside the
    # container, then build the site. Keeps the large base.css out of git.
    docker run --rm \
        -v "$ROOT/books/":/app/books \
        -v "$ROOT/scripts/":/app/scripts:ro \
        -e BASE_URL="/$book" \
        -w "/app/books/$book" \
        "$IMAGE" \
        sh -c "python3 /app/scripts/embed_fonts.py . && jupyter book build --html"

    echo "Publishing to static/$book/ ..."
    rm -rf "${STATIC:?}/$book"
    mkdir -p "$STATIC/$book"
    cp -R "$dir/_build/html/." "$STATIC/$book/"
    built=$((built + 1))
done

echo "Done. Built $built book(s) into static/."
