FROM python:3.11-slim-bullseye

LABEL Name="BSM2 in Python" Version=0.1.0
LABEL org.opencontainers.image.source = "https://gitlab.rrze.fau.de/evt/klaeffizient/bsm2-python"

WORKDIR /src
RUN apt update && apt install make

COPY . ./src
RUN make venv