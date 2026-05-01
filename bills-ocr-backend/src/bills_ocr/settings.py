from pathlib import Path
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BILLS_", env_file=".env", extra="ignore")

    ollama_base_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "phi4-mini"
    ollama_timeout_s: float = 120.0

    #: When set (e.g. `http://tesseract:8080`), OCR runs via HTTP to this service instead of local `pytesseract`.
    ocr_service_url: str | None = None
    ocr_service_timeout_s: float = 120.0

    data_dir: Path = Path("data")
    uploads_subdir: str = "uploads"
    db_filename: str = "bills.sqlite3"

    #: Downscale wide scans before OCR (pixels).
    preprocess_max_width: int = 2400
    #: Upscale narrow exports so text height is usable for Tesseract (~150–300 DPI equivalent).
    preprocess_min_width: int = 1400

    #: ``document``: grayscale + CLAHE (better for invoices / shaded tables). ``receipt``: Otsu binarize (thermal receipts).
    ocr_preprocess_mode: Literal["document", "receipt"] = "document"

    ocr_lang: str = "eng"
    #: Tesseract page segmentation; 6 = uniform block (typical invoices), 3 = fully automatic.
    ocr_psm: int = Field(default=6, ge=0, le=13)
    ocr_oem: int = Field(default=3, ge=0, le=3)

    @field_validator("ocr_service_url", mode="before")
    @classmethod
    def blank_ocr_url_none(cls, v: Any) -> str | None:
        if v is None:
            return None
        if isinstance(v, str) and not v.strip():
            return None
        return v

    @property
    def uploads_dir(self) -> Path:
        p = self.data_dir / self.uploads_subdir
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def db_path(self) -> Path:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        return self.data_dir / self.db_filename


settings = Settings()
