"""
IntelliJudge — Upload Pydantic Schemas

These schemas document and validate the shape of data returned by
the upload endpoints. They are also used to generate the Swagger
response documentation automatically.
"""

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    """
    Returned by POST /api/upload/screenshot.

    After receiving this, the client should call:
        POST /api/problems/reconstruct
    with the problem_id to trigger AI reconstruction.
    """

    problem_id: uuid.UUID
    screenshot_url: str      # Cloudinary CDN URL
    ocr_text: str            # Cleaned OCR-extracted text
    text_length: int         # Character count (useful for debugging OCR quality)

    model_config = ConfigDict(from_attributes=True)


class OCRResultResponse(BaseModel):
    """
    Returned by GET /api/upload/{problem_id}/ocr-result.

    screenshot_url and ocr_text may be None if the problem was created
    without an upload (e.g. manually typed).
    """

    problem_id: uuid.UUID
    screenshot_url: Optional[str]
    ocr_text: Optional[str]
    text_length: int

    model_config = ConfigDict(from_attributes=True)
