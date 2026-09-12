# CLI-first image: core deps + system OCR/PDF/audio tools, no GUI, no ML.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-fas tesseract-ocr-eng \
    poppler-utils ffmpeg \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY examples ./examples

ENTRYPOINT ["python", "-m", "app.cli"]
CMD ["--help"]
