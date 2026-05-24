"""
IntelliJudge — OCR Service

Full pipeline:
  UploadFile  →  Cloudinary (CDN storage)  →  EasyOCR (text extraction)  →  cleanup  →  str

ARCHITECTURE NOTES:
  - Cloudinary SDK is synchronous  → run in asyncio.to_thread() to avoid blocking the event loop
  - EasyOCR reader is CPU-bound and heavy → lazy singleton + asyncio.to_thread()
  - EasyOCR downloads ~100MB English model on first use (one-time, cached in ~/.EasyOCR/)
  - Text cleanup is fast/pure          → runs inline, no threading needed

DEPENDENCIES:
  cloudinary, easyocr, Pillow must be installed (see requirements.txt).
  Models are downloaded automatically on first call to extract_text_from_image().
"""

import asyncio
import io
import re
from typing import Optional

from fastapi import UploadFile

from app.config import settings
from app.utils.exceptions import BadRequestException

# ── File validation constants ──────────────────────────────────

ALLOWED_CONTENT_TYPES = frozenset({
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/gif",
    "image/bmp",
    "image/webp",
    "image/tiff",
})

MAX_FILE_SIZE_MB = 10
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


# ── File validation ────────────────────────────────────────────

def validate_upload_file(file: UploadFile, file_bytes: bytes) -> None:
    """
    Validate the uploaded file type and size.
    Raises BadRequestException (400) on failure so FastAPI returns it cleanly.
    """
    if not file.content_type or file.content_type.lower() not in ALLOWED_CONTENT_TYPES:
        raise BadRequestException(
            f"Unsupported file type: {file.content_type!r}. "
            "Please upload a JPEG, PNG, GIF, BMP, WEBP, or TIFF image."
        )
    if len(file_bytes) == 0:
        raise BadRequestException("Uploaded file is empty.")
    if len(file_bytes) > MAX_FILE_SIZE_BYTES:
        size_mb = len(file_bytes) / (1024 * 1024)
        raise BadRequestException(
            f"File too large ({size_mb:.1f} MB). Maximum allowed size is {MAX_FILE_SIZE_MB} MB."
        )


# ── Cloudinary upload ──────────────────────────────────────────

def _is_cloudinary_configured() -> bool:
    return bool(
        settings.CLOUDINARY_CLOUD_NAME
        and settings.CLOUDINARY_CLOUD_NAME not in ("", "your-cloud-name")
        and settings.CLOUDINARY_API_KEY
        and settings.CLOUDINARY_API_SECRET
    )


async def upload_to_cloudinary(file_bytes: bytes, original_filename: str) -> str:
    """
    Upload image bytes to Cloudinary and return the CDN URL.

    Wraps the synchronous Cloudinary SDK in asyncio.to_thread() so it
    doesn't block FastAPI's async event loop during the HTTP upload.

    Raises BadRequestException (400) if Cloudinary credentials are missing.
    """
    if not _is_cloudinary_configured():
        raise BadRequestException(
            "Cloudinary is not configured. "
            "Add CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, and CLOUDINARY_API_SECRET "
            "to your .env file. Sign up free at https://cloudinary.com"
        )

    import cloudinary
    import cloudinary.uploader

    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )

    def _do_upload() -> str:
        result = cloudinary.uploader.upload(
            file_bytes,
            folder="intellijudge/screenshots",
            resource_type="image",
            overwrite=False,
        )
        return result["secure_url"]

    return await asyncio.to_thread(_do_upload)


# ── EasyOCR — lazy singleton reader ────────────────────────────
# The Reader object is ~200MB in memory and takes 5-10s to initialize.
# We create it once on first use and reuse it for all subsequent requests.

_ocr_reader = None


def _get_ocr_reader():
    """Return the shared EasyOCR reader, initializing it on first call."""
    global _ocr_reader
    if _ocr_reader is None:
        try:
            import easyocr
        except ImportError as exc:
            raise RuntimeError(
                "EasyOCR is not installed. Run: pip install easyocr"
            ) from exc

        # gpu=False  → CPU inference (works everywhere, no CUDA required)
        # verbose=False → suppress progress bars in server logs
        # English model (~100MB) is downloaded automatically on first use
        _ocr_reader = easyocr.Reader(["en"], gpu=False, verbose=False)

    return _ocr_reader


# ── EasyOCR text extraction ────────────────────────────────────

async def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Run EasyOCR on the image and return the extracted raw text.

    EasyOCR's readtext() is CPU-bound and can take 2-10 seconds depending
    on image size. We run it in asyncio.to_thread() to keep the event loop
    responsive for other requests during extraction.

    Returns an empty string if no text is detected.
    """

    def _run_ocr() -> str:
        import numpy as np
        from PIL import Image

        reader = _get_ocr_reader()

        # Normalise to RGB numpy array — EasyOCR accepts numpy arrays, bytes, or
        # file paths, but NOT PIL Image objects directly.
        image = Image.open(io.BytesIO(image_bytes))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        image_np = np.array(image)

        # readtext returns [(bounding_box, text, confidence), ...]
        # paragraph=False → keep individual text regions (better for code problems)
        results = reader.readtext(image_np, detail=1, paragraph=False)

        # Filter out low-confidence detections (below 30%)
        # and join remaining lines in reading order (top-to-bottom, left-to-right)
        lines = [text for (_, text, conf) in results if conf >= 0.3]
        return "\n".join(lines)

    return await asyncio.to_thread(_run_ocr)


# ── Text cleanup ───────────────────────────────────────────────

def clean_ocr_text(raw_text: str) -> str:
    """
    Post-process raw EasyOCR output into clean, readable problem text.

    What it fixes:
      - Removes invisible Unicode characters (zero-width spaces, BOM, soft hyphens)
      - Strips leading/trailing whitespace from each line
      - Collapses runs of 3+ spaces into a double space (preserves alignment cues)
      - Collapses 3+ consecutive blank lines into a single blank line
      - Returns empty string if input is empty/whitespace-only
    """
    if not raw_text or not raw_text.strip():
        return ""

    lines = raw_text.split("\n")
    cleaned = []

    for line in lines:
        line = line.strip()
        # Remove invisible Unicode characters
        line = re.sub(r"[​‌‍﻿­]", "", line)
        # Collapse excessive spaces (preserve double-space for alignment)
        line = re.sub(r" {3,}", "  ", line)
        cleaned.append(line)

    text = "\n".join(cleaned)
    # Max 2 consecutive blank lines between sections
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()
