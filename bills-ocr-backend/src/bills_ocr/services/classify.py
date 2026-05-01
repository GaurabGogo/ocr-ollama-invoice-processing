"""Rule-based category refinement from vendor, purpose, and OCR text."""

from __future__ import annotations

import re

from bills_ocr.schemas import BillCategory, BillStructured


_RULES: list[tuple[BillCategory, tuple[str, ...]]] = [
    (
        BillCategory.FOOD,
        (
            "restaurant",
            "cafe",
            "coffee",
            "grocery",
            "supermarket",
            "bakery",
            "mcdonald",
            "starbucks",
            "pizza",
            "food",
            "lunch",
            "dinner",
        ),
    ),
    (
        BillCategory.TRANSPORT,
        (
            "uber",
            "lyft",
            "taxi",
            "fuel",
            "gas station",
            "parking",
            "transit",
            "metro",
            "train ticket",
            "airline",
            "car rental",
        ),
    ),
    (
        BillCategory.OFFICE,
        (
            "staples",
            "office depot",
            "stationery",
            "printer ink",
            "postage",
            "fedex",
            "dhl",
            "ups store",
        ),
    ),
    (
        BillCategory.UTILITIES,
        (
            "electric",
            "water bill",
            "internet",
            "broadband",
            "gas bill",
            "utility",
            "sewer",
            "trash",
        ),
    ),
    (
        BillCategory.HEALTHCARE,
        (
            "pharmacy",
            "hospital",
            "clinic",
            "dental",
            "medical",
            "prescription",
            "cvs",
            "walgreens",
        ),
    ),
    (
        BillCategory.ENTERTAINMENT,
        (
            "cinema",
            "movie",
            "theater",
            "theatre",
            "netflix",
            "spotify",
            "concert",
            "game",
            "steam",
        ),
    ),
    (
        BillCategory.SHOPPING,
        (
            "amazon",
            "target",
            "walmart",
            "retail",
            "electronics",
            "clothing",
            "apparel",
        ),
    ),
]


def refine_category(data: BillStructured, ocr_text: str) -> BillCategory:
    """Apply keyword rules on combined text; upgrade weak categories when confident."""

    parts: list[str] = []
    if data.vendor:
        parts.append(data.vendor)
    if data.purpose:
        parts.append(data.purpose)
    parts.append(ocr_text or "")
    blob = " ".join(parts)
    blob_norm = re.sub(r"\s+", " ", blob).strip()

    inferred: BillCategory | None = None
    best_hits = 0
    for cat, keywords in _RULES:
        hits = sum(1 for k in keywords if k in blob_norm.lower())
        if hits > best_hits:
            best_hits = hits
            inferred = cat

    current = data.category
    weak = current == BillCategory.OTHER or current is None

    if inferred is not None and best_hits >= 1:
        if weak or inferred != BillCategory.OTHER:
            return inferred

    return current
