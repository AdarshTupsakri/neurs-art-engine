"""Upload validation: size cap, real image decoding, and dimension normalisation."""
import io

from fastapi import HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import settings

ALLOWED_FORMATS = {"PNG", "JPEG", "WEBP"}


async def read_upload_image(file: UploadFile) -> Image.Image:
    data = await file.read(settings.MAX_UPLOAD_BYTES + 1)
    if len(data) > settings.MAX_UPLOAD_BYTES:
        raise HTTPException(413, f"Upload exceeds {settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB")
    if not data:
        raise HTTPException(400, "Uploaded file is empty")

    try:
        img = Image.open(io.BytesIO(data))
        img.verify()  # detects truncated / non-image payloads
        img = Image.open(io.BytesIO(data))  # verify() invalidates the handle
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(415, "File is not a valid image") from exc

    if img.format not in ALLOWED_FORMATS:
        raise HTTPException(415, f"Unsupported format {img.format}; use PNG, JPEG or WEBP")

    img = img.convert("RGB")
    img.thumbnail((settings.MAX_IMAGE_SIDE, settings.MAX_IMAGE_SIDE), Image.LANCZOS)
    return img
