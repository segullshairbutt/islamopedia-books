FROM python:3.12.7-slim-bullseye
WORKDIR /app

# Installing uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copying the pyproject.toml and uv.lock files
COPY pyproject.toml uv.lock /app/

# Install dependencies into /app/.venv
RUN uv sync --frozen --no-dev

# Put the project's virtualenv on PATH so `jupyter-book` is available directly
ENV PATH="/app/.venv/bin:$PATH"
