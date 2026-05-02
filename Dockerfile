# Use uv for fast Python dependency management
FROM astral/uv:python3.13-bookworm-slim

# Install vim and other utilities
RUN apt-get update && \
    apt-get install -y --no-install-recommends vim && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Set environment variables for uv
ENV UV_SYSTEM_PYTHON=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Copy requirements first for better layer caching
COPY src/backend/requirements.txt .

# Install dependencies using uv (much faster than pip)
RUN uv pip install --system --no-cache -r requirements.txt

# Install linting tools
RUN uv pip install --system --no-cache ruff pylint

# Copy the entire project structure
COPY . .

EXPOSE 5000
