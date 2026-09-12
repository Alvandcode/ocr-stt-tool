# CLI-first image: core deps + system OCR/PDF/audio tools, no GUI, no ML.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr tesseract-ocr-fas tesseract-ocr-eng \
    poppler-utils ffmpeg \
 && rm -rf /var/lib/apt/lists/* \
 && useradd -m -u 10001 ocrstt

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
 && pip install --no-cache-dir pytest \
 && python -m compileall -q app

COPY app ./app
COPY examples ./examples
COPY tests ./tests
RUN python -m pytest -q

USER ocrstt
ENTRYPOINT ["python", "-m", "app.cli"]
CMD ["--help"]
