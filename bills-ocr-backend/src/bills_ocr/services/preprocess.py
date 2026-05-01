"""OpenCV preprocessing before OCR."""

from __future__ import annotations

import numpy as np

from bills_ocr.settings import settings


def preprocess_for_ocr(image_bgr: np.ndarray) -> np.ndarray:
    import cv2

    if image_bgr.ndim != 3 or image_bgr.shape[2] != 3:
        raise ValueError("Expected BGR image with 3 channels")

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape[:2]

    max_w = settings.preprocess_max_width
    min_w = settings.preprocess_min_width

    if w > max_w:
        scale = max_w / float(w)
        new_w = max_w
        new_h = max(1, int(round(h * scale)))
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_AREA)
        h, w = gray.shape[:2]
    elif w < min_w:
        scale = min_w / float(w)
        new_w = min_w
        new_h = max(1, int(round(h * scale)))
        gray = cv2.resize(gray, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        h, w = gray.shape[:2]

    denoised = cv2.fastNlMeansDenoising(gray, h=8, templateWindowSize=7, searchWindowSize=21)

    if settings.ocr_preprocess_mode == "receipt":
        blur = cv2.GaussianBlur(denoised, (3, 3), 0)
        _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    # document: keep grayscale — avoids wrecking shaded cells / logos vs global Otsu
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(denoised)
