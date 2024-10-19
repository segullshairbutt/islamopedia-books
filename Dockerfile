FROM python:3.12.7-slim-bullseye
WORKDIR /app
# Installing poetry
RUN pip install poetry==1.8.3

# Copying the poetry.lock and pyproject.toml files
COPY pyproject.toml poetry.lock /app/

# Do not create a virtualenv
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install
