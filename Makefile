# It is a simple makefile to build the book using jupyter-book

# It checks if the book name is provided or not, if not it will use the default book name.
BOOK_NAME ?= template_book
# It checks if the image name is provided or not, if not it will use the default image name.
IMAGE_NAME ?= islamopedia-books

build_book:
	echo "Building book..."
	$(PWD)/.venv/bin/jupyter-book build --all books/${BOOK_NAME}
build_docker_image:
	echo "Building docker image..."
	docker build -t $(IMAGE_NAME) .
build_book_via_docker:
	echo "Building book via docker..."
	if ! docker image inspect $(IMAGE_NAME) > /dev/null 2>&1; then \
        $(MAKE) build_docker_image; \
    fi
	docker run --rm -v $(PWD)/books/:/app/books -t islamopedia-books jupyter-book build --all /app/books/${BOOK_NAME}
	