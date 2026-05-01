from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from bills_ocr.schemas import BillStructured


def _utc_now_iso() -> str:
    return datetime.now(tz=UTC).isoformat()


@dataclass
class BillRow:
    id: str
    created_at: str
    original_filename: str
    image_path: str
    ocr_text: str
    structured_json: dict[str, Any]
    validation_warnings_json: str


def init_db(db_path: Path) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bills (
                id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                original_filename TEXT NOT NULL,
                image_path TEXT NOT NULL,
                ocr_text TEXT NOT NULL,
                structured_json TEXT NOT NULL,
                validation_warnings TEXT NOT NULL DEFAULT '[]'
            )
            """
        )
        conn.commit()


def insert_bill(
    db_path: Path,
    *,
    original_filename: str,
    image_path: str,
    ocr_text: str,
    structured: BillStructured,
    validation_warnings: list[str],
    bill_id: str | None = None,
) -> str:
    bid = bill_id or str(uuid.uuid4())
    payload = structured.model_dump(mode="json")
    payload["category"] = structured.category.value
    warnings_json = json.dumps(validation_warnings)
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO bills (
              id, created_at, original_filename, image_path, ocr_text,
              structured_json, validation_warnings
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                bid,
                _utc_now_iso(),
                original_filename,
                image_path,
                ocr_text,
                json.dumps(payload),
                warnings_json,
            ),
        )
        conn.commit()
    return bid


def get_bill(db_path: Path, bill_id: str) -> BillRow | None:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM bills WHERE id = ?", (bill_id,))
        row = cur.fetchone()
    if row is None:
        return None
    return BillRow(
        id=row["id"],
        created_at=row["created_at"],
        original_filename=row["original_filename"],
        image_path=row["image_path"],
        ocr_text=row["ocr_text"],
        structured_json=json.loads(row["structured_json"]),
        validation_warnings_json=row["validation_warnings"],
    )


def list_bills(db_path: Path) -> list[BillRow]:
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute("SELECT * FROM bills ORDER BY created_at DESC")
        rows = cur.fetchall()
    out: list[BillRow] = []
    for row in rows:
        out.append(
            BillRow(
                id=row["id"],
                created_at=row["created_at"],
                original_filename=row["original_filename"],
                image_path=row["image_path"],
                ocr_text=row["ocr_text"],
                structured_json=json.loads(row["structured_json"]),
                validation_warnings_json=row["validation_warnings"],
            )
        )
    return out


def row_to_public(row: BillRow):
    from bills_ocr.schemas import BillRecordPublic

    structured = BillStructured.model_validate(row.structured_json)
    warnings = json.loads(row.validation_warnings_json or "[]")
    return BillRecordPublic(
        id=row.id,
        created_at=row.created_at,
        original_filename=row.original_filename,
        ocr_text=row.ocr_text,
        structured=structured,
        validation_warnings=list(warnings),
    )
