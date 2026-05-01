from __future__ import annotations

import mimetypes
from pathlib import Path

from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response

from bills_ocr.database import get_bill, init_db, list_bills, row_to_public
from bills_ocr.schemas import BillListResponse, BillRecordPublic, BillUploadResponse
from bills_ocr.services.excel_export import bills_to_xlsx_bytes
from bills_ocr.exceptions import TesseractNotAvailableError
from bills_ocr.services.pipeline import process_and_store
from bills_ocr.settings import settings

router = APIRouter(prefix="/bills", tags=["bills"])

_ALLOWED_TYPES = frozenset(
    {"image/jpeg", "image/png", "image/webp", "image/tiff", "image/bmp", "image/x-ms-bmp"}
)


def _ensure_db() -> None:
    init_db(settings.db_path)


@router.post("/upload", response_model=BillUploadResponse)
async def upload_bill(file: UploadFile = File(...)) -> BillUploadResponse:
    _ensure_db()
    ct = (file.content_type or "").split(";")[0].strip().lower()
    if ct not in _ALLOWED_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported media type {file.content_type!r}; "
            "allowed: jpeg, png, webp, tiff, bmp",
        )
    raw = await file.read()
    if not raw:
        raise HTTPException(status_code=400, detail="Empty upload")

    try:
        bill_id, structured, ocr_text, warnings = await process_and_store(
            file_bytes=raw,
            original_filename=file.filename or "upload",
            db_path=settings.db_path,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except TesseractNotAvailableError as e:
        raise HTTPException(status_code=503, detail=str(e)) from e

    row = get_bill(settings.db_path, bill_id)
    if row is None:
        raise HTTPException(status_code=500, detail="Record missing after insert")

    pub = row_to_public(row)
    return BillUploadResponse(record=pub)


@router.get("/export/excel")
async def export_excel() -> Response:
    _ensure_db()
    rows = list_bills(settings.db_path)
    data = bills_to_xlsx_bytes(rows)
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": 'attachment; filename="bills_export.xlsx"'},
    )


@router.get("", response_model=BillListResponse)
@router.get("/", response_model=BillListResponse)
async def list_all() -> BillListResponse:
    _ensure_db()
    rows = list_bills(settings.db_path)
    return BillListResponse(records=[row_to_public(r) for r in rows])


def _resolved_bill_image_path(row_image_path: str) -> Path:
    path = Path(row_image_path).expanduser().resolve()
    root = settings.uploads_dir.resolve()
    path.relative_to(root)
    return path


@router.get("/{bill_id}/image")
async def get_bill_image(bill_id: str) -> FileResponse:
    _ensure_db()
    row = get_bill(settings.db_path, bill_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    try:
        path = _resolved_bill_image_path(row.image_path)
    except ValueError:
        raise HTTPException(status_code=403, detail="Invalid image path") from None
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Image file missing")
    mime, _ = mimetypes.guess_type(path.name)
    media = mime or "application/octet-stream"
    return FileResponse(path, media_type=media, filename=path.name)


@router.get("/{bill_id}", response_model=BillRecordPublic)
async def get_one(bill_id: str) -> BillRecordPublic:
    _ensure_db()
    row = get_bill(settings.db_path, bill_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Bill not found")
    return row_to_public(row)
