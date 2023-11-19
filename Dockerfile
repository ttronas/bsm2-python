FROM python:3.11-slim-bullseye

LABEL Name="BSM2 in Python" Version=1.0.0
LABEL org.opencontainers.image.source = "https://gitlab.rrze.fau.de/evt/klaeffizient/bsm2-python"

ARG srcDir=src
WORKDIR /src
COPY $srcDir/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY $srcDir/ ./src