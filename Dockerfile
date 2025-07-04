# syntax=docker/dockerfile:1

FROM python:3.13-slim

# Install uv (modern Python package manager)
RUN pip install --upgrade pip && pip install uv

# Set work directory
WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv pip install --system --no-cache-dir .

# Copy the rest of the application
COPY . .

# Expose port for the server
EXPOSE 8000

# Healthcheck (adjust path if you have a health endpoint)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Set environment variable for DeepL API key (must be provided at runtime)
ENV DEEPL_AUTH_KEY=""

# Default command to run the server
# run with python remote_server.py

CMD ["uv", "run", "mcp", "run", "main.py"]
