# Bills API — includes local Tesseract for `pytesseract` when `BILLS_OCR_SERVICE_URL` is unset.
# With Docker Compose you can still point `BILLS_OCR_SERVICE_URL` at the separate `tesseract` service.
FROM python:3.12-slim-bookworm

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        tesseract-ocr \
        tesseract-ocr-eng \
        libglib2.0-0 \
        libgomp1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
COPY src ./src

RUN pip install --no-cache-dir .

ENV PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "bills_ocr.main:app", "--host", "0.0.0.0", "--port", "8000"]
