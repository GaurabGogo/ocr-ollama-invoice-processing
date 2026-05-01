"""Tesseract OCR via local binary or remote HTTP service."""

from __future__ import annotations

import asyncio
import io

import httpx
import numpy as np
from PIL import Image

from bills_ocr.exceptions import TesseractNotAvailableError
from bills_ocr.settings import settings


async def image_to_text(preprocessed_gray: np.ndarray) -> str:
    import pytesseract

    if preprocessed_gray.ndim != 2:
        raise ValueError("Expected single-channel image for OCR")

    pil = Image.fromarray(preprocessed_gray)
    cfg = f"--oem {settings.ocr_oem} --psm {settings.ocr_psm}"

    base = settings.ocr_service_url
    if base:
        buf = io.BytesIO()
        pil.save(buf, format="PNG")
        png = buf.getvalue()
        url = base.rstrip("/") + "/ocr"
        try:
            async with httpx.AsyncClient(timeout=settings.ocr_service_timeout_s) as client:
                res = await client.post(
                    url,
                    files={"file": ("ocr.png", png, "image/png")},
                    data={
                        "lang": settings.ocr_lang,
                        "oem": str(settings.ocr_oem),
                        "psm": str(settings.ocr_psm),
                    },
                )
                res.raise_for_status()
        except httpx.HTTPError as e:
            raise TesseractNotAvailableError(
                f"OCR service unreachable or error ({url}): {e}"
            ) from e

        try:
            payload = res.json()
        except ValueError as e:
            raise TesseractNotAvailableError(
                "OCR service returned non-JSON body"
            ) from e

        text = payload.get("text")
        if text is None:
            raise TesseractNotAvailableError(
                "OCR service JSON missing 'text' field"
            )
        return str(text).strip()

    def run_local() -> str:
        return pytesseract.image_to_string(
            pil,
            lang=settings.ocr_lang,
            config=cfg,
        ).strip()

    try:
        return await asyncio.to_thread(run_local)
    except pytesseract.TesseractNotFoundError as e:
        raise TesseractNotAvailableError(
            "Tesseract OCR is not installed or not on PATH; "
            "install `tesseract-ocr`, set `BILLS_OCR_SERVICE_URL` to a Tesseract HTTP service, "
            "or run via Docker Compose."
        ) from e
