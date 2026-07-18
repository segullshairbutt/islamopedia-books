# It is a simple makefile to build the book using Jupyter Book 2 (MyST).

# It checks if the book name is provided or not, if not it will use the default book name.
BOOK_NAME ?= template_book
# It checks if the image name is provided or not, if not it will use the default image name.
IMAGE_NAME ?= islamopedia-books

# Jupyter Book 2 reads myst.yml from the current directory, so each target runs
# from inside the book directory using the project's uv-managed virtualenv.
JB = $(PWD)/.venv/bin/jupyter book

# Regenerate the self-contained _static/base.css (fonts inlined as data: URIs).
# Run this whenever _static/base.src.css or the font files change.
embed_fonts:
	uv run python scripts/embed_fonts.py books/${BOOK_NAME}

# Build the static HTML site into books/${BOOK_NAME}/_build/html
build_book: embed_fonts
	echo "Building book..."
	cd books/${BOOK_NAME} && $(JB) build --html
	echo "Open books/${BOOK_NAME}/_build/html/index.html in your browser."

# Start a live-reloading dev server for local authoring (Ctrl-C to stop).
serve_book: embed_fonts
	echo "Starting live preview..."
	cd books/${BOOK_NAME} && $(JB) start

build_docker_image:
	echo "Building docker image..."
	docker build -t $(IMAGE_NAME) .
build_book_via_docker:
	echo "Building book via docker..."
	if ! docker image inspect $(IMAGE_NAME) > /dev/null 2>&1; then \
        $(MAKE) build_docker_image; \
    fi
	docker run --rm -v $(PWD)/books/:/app/books -w /app/books/${BOOK_NAME} -t $(IMAGE_NAME) jupyter book build --html
