"""
IntelliJudge — Upload Routes

Endpoints:
  POST /api/upload/screenshot          Upload image → Cloudinary → EasyOCR → partial Problem
  GET  /api/upload/{problem_id}/ocr-result  Retrieve stored OCR text for a problem

FLOW (Phase 4 → Phase 5):
  1. [Phase 4] POST /api/upload/screenshot
       → Stores image on Cloudinary
       → Runs EasyOCR to extract text
       → Creates a partial Problem (screenshot_url + ocr_text filled; AI fields pending)
       → Returns problem_id + ocr_text

  2. [Phase 5] POST /api/problems/reconstruct  (body: { problem_id })
       → Reads ocr_text from the Problem
       → Sends it to Google Gemini
       → Updates the Problem with title, description, difficulty, tags, examples, constraints

AUTHENTICATION:
  Both endpoints require a valid Bearer token (get it from /api/auth/login).
  A user can only access their own problems.
"""

import uuid

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.problem import Problem
from app.models.user import User
from app.services.ocr_service import (
    clean_ocr_text,
    extract_text_from_image,
    upload_to_cloudinary,
    validate_upload_file,
)
from app.utils.exceptions import NotFoundException, success_response
from app.utils.jwt import get_current_user

router = APIRouter()


@router.post(
    "/screenshot",
    status_code=201,
    summary="Upload a screenshot and extract text",
    description=(
        "Upload a screenshot of a coding problem. "
        "The image is stored in Cloudinary and EasyOCR extracts the text. "
        "A partial Problem record is created and returned with the OCR text. "
        "Call POST /api/problems/reconstruct with the returned problem_id to run AI reconstruction."
    ),
)
async def upload_screenshot(
    file: UploadFile = File(..., description="Image file (JPEG, PNG, GIF, BMP, WEBP, TIFF — max 10 MB)"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Full upload pipeline:
      1. Validate file type and size
      2. Upload to Cloudinary → get CDN URL
      3. Run EasyOCR on the image → raw text
      4. Clean up OCR text (remove artifacts, normalize whitespace)
      5. Create partial Problem in DB (AI fields filled in Phase 5)
      6. Return problem_id + ocr_text

    **Note:** EasyOCR downloads its English model (~100 MB) on first run.
    Subsequent calls are fast because the model stays in memory.
    """
    # Step 1 — read and validate
    file_bytes = await file.read()
    validate_upload_file(file, file_bytes)

    # Step 2 — upload to Cloudinary (runs in thread pool, non-blocking)
    screenshot_url = await upload_to_cloudinary(
        file_bytes,
        original_filename=file.filename or "screenshot.jpg",
    )

    # Step 3 + 4 — OCR extraction + cleanup (runs in thread pool, non-blocking)
    raw_text = await extract_text_from_image(file_bytes)
    ocr_text = clean_ocr_text(raw_text)

    # Step 5 — create partial Problem
    # title and description are placeholder values; Phase 5 will replace them.
    problem = Problem(
        user_id=current_user.id,
        screenshot_url=screenshot_url,
        ocr_text=ocr_text,
        title="Untitled Problem",
        description="AI reconstruction pending. Call POST /api/problems/reconstruct to generate the full problem statement.",
    )
    db.add(problem)
    await db.commit()
    await db.refresh(problem)

    return success_response(
        data={
            "problem_id": str(problem.id),
            "screenshot_url": screenshot_url,
            "ocr_text": ocr_text,
            "text_length": len(ocr_text),
        },
        message="Screenshot uploaded and text extracted successfully",
    )


@router.get(
    "/{problem_id}/ocr-result",
    summary="Get stored OCR result",
    description="Retrieve the OCR-extracted text for a previously uploaded screenshot. Only returns your own problems.",
)
async def get_ocr_result(
    problem_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetch the OCR text and screenshot URL stored for a Problem.

    Returns 404 if the problem doesn't exist or belongs to a different user.
    """
    result = await db.execute(
        select(Problem).where(
            Problem.id == problem_id,
            Problem.user_id == current_user.id,
        )
    )
    problem = result.scalar_one_or_none()

    if not problem:
        raise NotFoundException("Problem")

    return success_response(
        data={
            "problem_id": str(problem.id),
            "screenshot_url": problem.screenshot_url,
            "ocr_text": problem.ocr_text,
            "text_length": len(problem.ocr_text) if problem.ocr_text else 0,
        },
        message="OCR result retrieved",
    )
