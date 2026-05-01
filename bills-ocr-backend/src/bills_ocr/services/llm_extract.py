"""Call Ollama to extract strictly structured bill JSON from OCR text."""

from __future__ import annotations

import json
import re
from typing import Any

import httpx

from bills_ocr.settings import settings


SYSTEM_PROMPT = """You extract structured data from receipt OCR text.
Respond with ONE JSON object only. No markdown, no explanation, no code fences.
Keys exactly: "date", "vendor", "amount", "quantity", "purpose", "category".
Use null for unknown values.
category must be one of: food, transport, office, utilities, healthcare, entertainment, shopping, other.
amount is the JSON number for total paid (use a dot as decimal separator, e.g. 425.42 not 425,42).
quantity is a JSON number when clearly indicated (items/units), else null.
date as ISO yyyy-mm-dd when possible."""

USER_TEMPLATE = """OCR text:
---
{text}
---
Return only the JSON object."""


def _strip_json_fence(raw: str) -> str:
    s = raw.strip()
    if s.startswith("```"):
        s = re.sub(r"^```(?:json)?\s*", "", s, flags=re.IGNORECASE)
        s = re.sub(r"\s*```$", "", s)
    return s.strip()


def _extract_first_json_object(raw: str) -> dict[str, Any]:
    s = _strip_json_fence(raw)
    try:
        obj = json.loads(s)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    start = s.find("{")
    end = s.rfind("}")
    if start >= 0 and end > start:
        chunk = s[start : end + 1]
        obj = json.loads(chunk)
        if isinstance(obj, dict):
            return obj
    raise ValueError("Model output did not contain a JSON object")


async def extract_structured_fields(ocr_text: str) -> dict[str, Any]:
    prompt = USER_TEMPLATE.format(text=ocr_text[:12000])
    url = settings.ollama_base_url.rstrip("/") + "/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": SYSTEM_PROMPT + "\n\n" + prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1},
    }
    async with httpx.AsyncClient(timeout=settings.ollama_timeout_s) as client:
        try:
            r = await client.post(url, json=payload)
            r.raise_for_status()
        except httpx.HTTPError as e:
            base = settings.ollama_base_url.rstrip("/")
            model = settings.ollama_model
            hint = (
                f"Cannot reach Ollama at {base} ({e}). "
                f"If the API runs in Docker, use Compose with an `ollama` service "
                f"and set BILLS_OLLAMA_BASE_URL=http://ollama:11434, or run Ollama on the host "
                f"with OLLAMA_HOST=0.0.0.0:11434 so host.docker.internal works. "
                f"Otherwise start Ollama locally (`ollama serve`) and run `ollama pull {model}`."
            )
            raise RuntimeError(hint) from e

    body = r.json()
    raw = body.get("response", "")
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("Empty response from Ollama")

    try:
        return _extract_first_json_object(raw)
    except (json.JSONDecodeError, ValueError) as e:
        raise ValueError(f"Could not parse JSON from model: {raw[:500]}") from e
