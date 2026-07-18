# Builder image for the books. Jupyter Book 2 runs on the MyST engine, whose
# compiled JS ships inside the pip package but needs a Node.js runtime (v18, 20,
# or 22+). Debian bookworm provides Node.js 18, which satisfies that.
FROM python:3.12-slim-bookworm
WORKDIR /app

# Node.js runtime + npm required by Jupyter Book 2 / MyST (MyST checks for
# node >= 18 and npm >= 8.6 on startup). Debian ships nodejs and npm separately.
RUN apt-get update \
    && apt-get install -y --no-install-recommends nodejs npm ca-certificates procps \
    && rm -rf /var/lib/apt/lists/*

# uv for dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install Python dependencies (Jupyter Book 2) into /app/.venv
COPY pyproject.toml uv.lock /app/
RUN uv sync --frozen --no-dev

# Put the project's virtualenv on PATH so `jupyter book` is available directly.
ENV PATH="/app/.venv/bin:$PATH"
