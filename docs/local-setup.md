# Running the project locally
There are two ways to run the project locally. One is to use the Docker container and the other is to use the Python environment. 

## Recommended Setup
Following are the recommended setups for running the project locally:
1. Use the Docker container if you don't want to install the dependencies on your machine. For installation instructions, visit the [Docker website](https://docs.docker.com/get-docker/).
2. You should have `make` installed on your machine to run the commands easily. For installation instructions, visit the [GNU Make website](https://www.gnu.org/software/make/). For windows installation, you can either use the [Chocolatey package manager](https://chocolatey.org/) or install through [winget](https://stackoverflow.com/a/73862277)
3. Use the VSCode editor for development. It has a lot of features that can help you in writing the books. For installation instructions, visit the [VSCode website](https://code.visualstudio.com/).
4. Install the [Run on Save](https://marketplace.visualstudio.com/items?itemName=emeraldwalk.RunOnSave) extension in VSCode to auto-build the book on save.
5. Use the [Live Server](https://marketplace.visualstudio.com/items?itemName=ritwickdey.LiveServer) extension in VSCode to view the book in the browser in real-time.

## Using Local Python Environment
We are using Poetry to manage the dependencies of the project. To setup the project locally, follow the steps below:
1. Install python>3.12 and poetry==1.8.3, preferably using [pyenv](https://github.com/pyenv/pyenv)
2. Create a virtual environment and install dependencies using:
    ```bash
    poetry install
    ```
    2.1. If you want to create a virtual environment directory in the project, use the following command:
    ```bash
    poetry config virtualenvs.in-project true
    ```
    For more information, visit the [Poetry documentation](https://python-poetry.org/docs/configuration/#virtualenvsin-project).
3. Activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```
4. To build the book, you need to run the following command:
    ```bash
    poetry run jupyter-book build BOOK_PATH
    ```
    Replace `BOOK_PATH` with the path of the book you want to build. If you want to build the `template_book`, you can use the following command:
    ```bash
    poetry run jupyter-book build books/template_book
    ```
    Or If you want to build the book using the `make` command, you can use the following command:
    ```bash
    make build_book BOOK_NAME=template_book
    ```

And you can open the index.html file in your browser in the _build directory to view the book.

## Using Docker (Recommended)
To run the project using Docker, you need to have Docker installed on your machine. Follow the steps below to run the project using Docker:
1. Build the Docker image using the following command:
    ```bash
    docker build -t islamopedia-books .
    ```
    Or you can use the following command if you have `make` installed on your machine:
    ```bash
    make build_docker_image
    ```
2. Build the book using the following command:
    ```bash
    docker run --rm -v $(PWD)/books/:/app/books -t islamopedia-books jupyter-book build --all /app/books/${BOOK_NAME}
    ```
    Or you can use the following command if you have `make` installed on your machine:
    ```bash
    make build_book_via_docker BOOK_NAME=${BOOK_NAME}
    ```
    Replace `${BOOK_NAME}` with the name of the book you want to build. If no book name is provided, it will build the `template_book` by default.

## VSCode settings for Auto-Build
The development experience can be improved by using the auto-build feature of VSCode. To enable this feature, you have to install [Run on Save](https://marketplace.visualstudio.com/items?itemName=emeraldwalk.RunOnSave) extension and add the following settings to the `.vscode/settings.json` file:
```json
{
    "python.defaultInterpreterPath": "",
    "emeraldwalk.runonsave": {
        "commands": [
            {
                "match": "\\.md|.yml|.css$",
                "cmd": COMMAND_TO_BUILD_BOOK
            }
        ]
    }
}
```

Replace `COMMAND_TO_BUILD_BOOK` with the command to build the book. It could be either the command to build the book using the Python environment or the Docker container. You can use the any command based on your setup as they are mentioned above.

NOTE: We are using `--all` flag to build the entire book. If you want to build only the changed files, you can remove the `--all` flag from the command. It should be removed from `Makefile` if you are using the `make` command to build the book.
 