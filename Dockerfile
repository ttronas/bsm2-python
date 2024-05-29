FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

COPY .. /bsm2-python
RUN chmod -R 777 /bsm2-python
RUN git config --global --add safe.directory /bsm2-python
RUN pip install pipx
RUN pipx install hatch
# now install all environments from pyproject.toml
WORKDIR /bsm2-python
RUN pipx install pre-commit
RUN hatch run pre-commit install
RUN hatch env create test
# RUN hatch env create docs
# RUN hatch env create lint
