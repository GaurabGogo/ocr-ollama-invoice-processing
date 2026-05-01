"""End-to-end processing: decode image → preprocess → OCR → LLM → validate → classify."""

from __future__ import annotations

import uuid
from pathlib import Path

import numpy as np

from bills_ocr.database import insert_bill
from bills_ocr.schemas import BillStructured
from bills_ocr.services.classify import refine_category
from bills_ocr.services.llm_extract import extract_structured_fields
from bills_ocr.services.ocr_service import image_to_text
from bills_ocr.services.preprocess import preprocess_for_ocr
from bills_ocr.settings import settings


def decode_upload_bytes(data: bytes) -> np.ndarray:
    import cv2

    arr = np.frombuffer(data, dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError("Could not decode image bytes (unsupported or corrupt file)")
    return img


def collect_validation_warnings(data: BillStructured, ocr_text: str) -> list[str]:
    warnings: list[str] = []
    if not (data.vendor or "").strip():
        warnings.append("vendor missing or empty")
    if data.amount is None:
        warnings.append("amount missing or unparsable")
    if not (data.date or "").strip():
        warnings.append("date missing or unparsable")
    if not ocr_text.strip():
        warnings.append("OCR produced no text")
    return warnings


async def process_and_store(
    *,
    file_bytes: bytes,
    original_filename: str,
    db_path: Path,
) -> tuple[str, BillStructured, str, list[str]]:
    image_bgr = decode_upload_bytes(file_bytes)

    ext = Path(original_filename).suffix or ".png"
    safe_name = f"{uuid.uuid4().hex}{ext}"
    dest = settings.uploads_dir / safe_name
    dest.write_bytes(file_bytes)
    image_abs_path = str(dest.resolve())

    pre = preprocess_for_ocr(image_bgr)
    ocr_text = await image_to_text(pre)
    raw_fields = await extract_structured_fields(ocr_text)

    structured = BillStructured.model_validate(raw_fields)
    structured = structured.model_copy(update={"category": refine_category(structured, ocr_text)})
    warnings = collect_validation_warnings(structured, ocr_text)

    bill_id = insert_bill(
        db_path,
        original_filename=original_filename,
        image_path=image_abs_path,
        ocr_text=ocr_text,
        structured=structured,
        validation_warnings=warnings,
    )
    return bill_id, structured, ocr_text, warnings
