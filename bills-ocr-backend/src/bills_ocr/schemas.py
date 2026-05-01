from __future__ import annotations

import re
from datetime import date, datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BillCategory(str, Enum):
    FOOD = "food"
    TRANSPORT = "transport"
    OFFICE = "office"
    UTILITIES = "utilities"
    HEALTHCARE = "healthcare"
    ENTERTAINMENT = "entertainment"
    SHOPPING = "shopping"
    OTHER = "other"


def _normalize_decimal_string(raw: str) -> float | None:
    """Parse totals/lines with US or European formatting (comma decimal, dot thousands)."""
    s = raw.strip().replace("\xa0", " ").replace("\u202f", " ")
    if not s or not re.search(r"\d", s):
        return None

    neg = False
    if s.startswith("(") and s.endswith(")"):
        neg = True
        s = s[1:-1].strip()
    s = s.replace("\u2212", "-").replace("−", "-")
    if s.startswith("-"):
        neg = True
        s = s[1:].strip()

    s = re.sub(r"[\u20ac£¥$]", "", s)
    s = s.replace(" ", "")

    if "," in s and "." in s:
        if s.rfind(",") > s.rfind("."):
            s = s.replace(".", "").replace(",", ".")
        else:
            s = s.replace(",", "")
    elif "," in s:
        parts = s.split(",")
        if len(parts) == 2 and len(parts[1]) <= 2:
            int_part = parts[0].replace(".", "")
            s = int_part + "." + parts[1]
        else:
            s = "".join(parts)
    elif "." in s:
        parts = s.split(".")
        if len(parts) > 2:
            s = "".join(parts[:-1]) + "." + parts[-1]

    try:
        v = float(s)
        return -v if neg else v
    except ValueError:
        return None


def _parse_amount(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    return _normalize_decimal_string(s)


def _parse_quantity(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    s = str(value).strip()
    if not s:
        return None
    whole = _normalize_decimal_string(s)
    if whole is not None:
        return whole
    m = re.search(r"-?[\d][\d.,]*", s)
    if not m:
        return None
    return _normalize_decimal_string(m.group(0))


def _normalize_date(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, datetime):
        return value.date().isoformat()
    s = str(value).strip()
    if not s:
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s[:10] if len(s) >= 10 else s, fmt).date().isoformat()
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).date().isoformat()
    except ValueError:
        return None


class BillStructured(BaseModel):
    """Validated structured bill fields after AI + normalization."""

    model_config = ConfigDict(extra="ignore")

    date: str | None = None
    vendor: str | None = None
    amount: float | None = None
    quantity: float | None = None
    purpose: str | None = None
    category: BillCategory = BillCategory.OTHER

    @field_validator("date", mode="before")
    @classmethod
    def coerce_date(cls, v: Any) -> str | None:
        return _normalize_date(v)

    @field_validator("vendor", "purpose", mode="before")
    @classmethod
    def coerce_str(cls, v: Any) -> str | None:
        if v is None:
            return None
        s = str(v).strip()
        return s or None

    @field_validator("amount", mode="before")
    @classmethod
    def coerce_amount(cls, v: Any) -> float | None:
        return _parse_amount(v)

    @field_validator("quantity", mode="before")
    @classmethod
    def coerce_quantity(cls, v: Any) -> float | None:
        return _parse_quantity(v)

    @field_validator("category", mode="before")
    @classmethod
    def coerce_category(cls, v: Any) -> BillCategory:
        if v is None:
            return BillCategory.OTHER
        s = str(v).strip().lower().replace(" ", "_").replace("-", "_")
        aliases = {
            "groceries": BillCategory.FOOD,
            "restaurant": BillCategory.FOOD,
            "dining": BillCategory.FOOD,
            "fuel": BillCategory.TRANSPORT,
            "gas": BillCategory.TRANSPORT,
            "parking": BillCategory.TRANSPORT,
            "uber": BillCategory.TRANSPORT,
            "taxi": BillCategory.TRANSPORT,
            "supplies": BillCategory.OFFICE,
            "subscription": BillCategory.UTILITIES,
            "internet": BillCategory.UTILITIES,
            "electric": BillCategory.UTILITIES,
            "water": BillCategory.UTILITIES,
            "pharmacy": BillCategory.HEALTHCARE,
            "medical": BillCategory.HEALTHCARE,
            "movie": BillCategory.ENTERTAINMENT,
            "streaming": BillCategory.ENTERTAINMENT,
            "retail": BillCategory.SHOPPING,
            "amazon": BillCategory.SHOPPING,
        }
        if s in aliases:
            return aliases[s]
        try:
            return BillCategory(s)
        except ValueError:
            return BillCategory.OTHER


class BillRecordPublic(BaseModel):
    id: str
    created_at: str
    original_filename: str
    ocr_text: str
    structured: BillStructured
    validation_warnings: list[str] = Field(default_factory=list)


class BillUploadResponse(BaseModel):
    record: BillRecordPublic


class BillListResponse(BaseModel):
    records: list[BillRecordPublic]
