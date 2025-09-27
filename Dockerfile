# Use a devcontainer base image instead of python:3.11-slim
FROM mcr.microsoft.com/devcontainers/python:3.11-bullseye

# Instala uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/

# Configura el entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Copia e instala dependencias
COPY pyproject.toml .
ENV UV_LINK_MODE=copy

RUN uv python install
RUN uv sync

# Directorio de trabajo
WORKDIR /workspaces/bsm2-python

# Copia el resto del código
COPY . .