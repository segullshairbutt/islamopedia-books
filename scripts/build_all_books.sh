#!/bin/bash

# docker build -t books-builder .
for dir in books/*/; do
    if [ -d "$dir" ]; then
        docker run --rm -v "$(pwd)/books/":/app/books books-builder jupyter-book build --path-output "/app/static/$(basename "$dir")" "/app/books/$(basename "$dir")"
    fi
done