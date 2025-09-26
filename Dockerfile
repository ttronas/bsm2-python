# Use a specific Python version for reproducibility
FROM python:3.11-slim as base

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/

# Set up environment
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Create a virtual environment
RUN python -m venv $VIRTUAL_ENV

# Copy and install Python dependencies
COPY pyproject.toml .
RUN uv pip install -p $VIRTUAL_ENV/bin/python --system-site-packages -r pyproject.toml

# Set working directory
WORKDIR /workspace

# Copy the rest of the application code
COPY . .