FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY dataforge dataforge
COPY sample_data sample_data
COPY pyproject.toml pyproject.toml
COPY README.md README.md

CMD ["python", "-m", "dataforge.cli", "run", "--input", "sample_data/input", "--output", "data"]
