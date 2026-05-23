FROM python:3.12-slim

# Set working directory in the container
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install uv using pip
RUN pip install --no-cache-dir uv

# Copy pyproject.toml and uv.lock (if exists) first to leverage Docker layer caching
COPY pyproject.toml uv.lock* ./

# Install Python dependencies using uv
RUN uv sync --frozen

# Copy the rest of the application code
COPY . .

# Create directories for temporary files and uploads
RUN mkdir -p /tmp/uploads /tmp/outputs

# Expose the port the app runs on
EXPOSE 5000

# Set the default command to run the Flask app using uv
CMD ["uv", "run", "python", "-m", "flask", "run", "--host=0.0.0.0", "--port=5000"]