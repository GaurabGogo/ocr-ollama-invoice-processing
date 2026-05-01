## Local (uvicorn)

```bash
cd bills-ocr
uv sync --group dev
# Needs: Tesseract OCR + Ollama; then:
ollama pull phi4-mini   # once
uv run uvicorn bills_ocr.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Compose

Pulls **`OLLAMA_MODEL`** (default **`phi4-mini`**) into the `ollama_data` volume whenever you run **`docker compose up`**, then starts the API.

```bash
cd bills-ocr
docker compose up --build -d
# Optional: OLLAMA_MODEL=llama3.2 docker compose up --build -d
```

SQLite and uploaded images are stored under **`./data`** on the host (bind-mounted into the API container).

If Ollama is already on the host instead, run **`ollama serve`** and **`ollama pull phi4-mini`** as above.

## OCR tuning (optional env)

Defaults favor printed invoices (grayscale + CLAHE, **`BILLS_OCR_PSM=6`**). For faint thermal receipts try **`BILLS_OCR_PREPROCESS_MODE=receipt`** (Otsu binarize).
