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


# ── Free OCR API: Google Cloud Vision (via pytesseract alternative)
# Using Tesseract OCR via pytesseract is lightweight (~50MB vs EasyOCR's 200MB)
# and works great on Render free tier.

import base64


async def extract_text_from_image(image_bytes: bytes) -> str:
    """
    Extract text from image using Google Cloud Vision API (free tier) or 
    fallback to Tesseract OCR if Vision API is not configured.
    
    Google Cloud Vision:
    - 1000 requests/month free
    - Much more accurate than local OCR
    - No local model loading (saves RAM)
    
    Returns empty string if no text detected.
    """
    # Try Google Cloud Vision API first (if credentials available)
    try:
        from google.cloud import vision
        from google.oauth2 import service_account
        
        # Check if service account JSON is available as environment variable
        import json
        import os
        
        if google_creds := os.getenv("GOOGLE_CLOUD_VISION_CREDENTIALS"):
            credentials = service_account.Credentials.from_service_account_info(
                json.loads(google_creds)
            )
            client = vision.ImageAnnotatorClient(credentials=credentials)
            image = vision.Image(content=image_bytes)
            response = client.text_detection(image=image)
            
            if response.text_annotations:
                # First annotation is full text
                return response.text_annotations[0].description
            return ""
    except Exception:
        pass  # Fall through to Tesseract
    
    # Fallback: Use Tesseract OCR (lightweight, ~50MB)
    def _run_tesseract_ocr() -> str:
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(io.BytesIO(image_bytes))
            # Preprocess: convert to grayscale for better OCR
            if image.mode != "L":
                image = image.convert("L")
            
            text = pytesseract.image_to_string(image)
            return text
        except ImportError:
            raise BadRequestException(
                "Tesseract OCR is not installed. "
                "Install it with: pip install pytesseract\n"
                "Also install Tesseract binary from: https://github.com/UB-Mannheim/tesseract/wiki"
            )
        except Exception as e:
            # If Tesseract fails, return placeholder
            return f"[OCR Error: {str(e)}]"
    
    return await asyncio.to_thread(_run_tesseract_ocr)


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
