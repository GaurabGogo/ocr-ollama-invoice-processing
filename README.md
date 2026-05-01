# Bill OCR

A small full-stack app for **uploading bill images**, running **OCR** (Tesseract) with optional **OpenCV preprocessing**, and **structuring fields** with a local **LLM via Ollama**. Data is stored in **SQLite**; images live under `data/uploads`. A **Next.js** UI lists bills, shows extracted details and the original image, supports uploads, and can trigger **Excel export**.

## Repository layout

| Path | Role |
|------|------|
| [`bills-ocr-backend/`](bills-ocr-backend/) | **FastAPI** service (`bills_ocr`): `/bills` upload, list, detail, image, Excel export; `/health`. |
| [`bill-ocr-frontend/`](bill-ocr-frontend/) | **Next.js** app with API routes that call the backend (`BILLS_API_URL`). |

## Prerequisites

- **Backend:** Python 3.11+, [uv](https://github.com/astral-sh/uv) (or pip), **Tesseract OCR** on the host (unless you configure a remote OCR HTTP service), **Ollama** with a pulled model (default **`phi4-mini`**).
- **Frontend:** Node.js 20+ (recommended), npm.

## Run the backend

From `bills-ocr-backend/`:

```bash
uv sync --group dev
ollama pull phi4-mini   # once, if using default model
uv run uvicorn bills_ocr.main:app --reload --host 0.0.0.0 --port 8000
```

Optional **Docker Compose** (API + Ollama + automatic model pull):

```bash
cd bills-ocr-backend
docker compose up --build -d
```

SQLite and uploads are under **`bills-ocr-backend/data`** (or `./data` relative to that compose project). More detail and OCR-related env vars are in [`bills-ocr-backend/README.md`](bills-ocr-backend/README.md).

Backend settings use the **`BILLS_`** prefix (see `bills_ocr/settings.py`), e.g. `BILLS_OLLAMA_BASE_URL`, `BILLS_OLLAMA_MODEL`, `BILLS_OCR_PREPROCESS_MODE`.

## Run the frontend

From `bill-ocr-frontend/`:

```bash
npm install
export BILLS_API_URL=http://127.0.0.1:8000   # default if unset
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Build for production with `npm run build` and `npm start`.

## Typical workflow

1. Start Ollama (and pull the model) and the FastAPI app on port **8000**.
2. Start the Next.js dev server on port **3000** with `BILLS_API_URL` pointing at the API.
3. Upload JPEG/PNG/WebP/TIFF/BMP bills via the UI; review extracted fields and export to Excel when needed.
