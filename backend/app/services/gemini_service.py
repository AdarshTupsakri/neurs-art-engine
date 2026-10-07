"""
Gemini integration: ONE generate_content call returns ONE sheet containing every stage.

The prompt asks for strict registration (same framing in every cell) and strict
continuation (cell k = cell k-1 + new marks). Models don't obey this perfectly, which is
why the sketch/paint engines *enforce* continuity afterwards instead of trusting the model.
"""
from __future__ import annotations

import io
import logging

from PIL import Image

from app.core.config import settings
from app.services.stages import MODE_STAGES, MODE_STYLE

logger = logging.getLogger("neurs.gemini")


class GeminiUnavailable(RuntimeError):
    """No API key configured, SDK missing, or the API call failed."""


def build_sheet_prompt(mode: str, subject: str | None, has_reference: bool, rows: int, cols: int) -> str:
    stages = MODE_STAGES[mode]
    cells = rows * cols
    subject_line = (
        "The subject is the attached reference image - reproduce its composition faithfully."
        if has_reference and not subject
        else f"The subject is: {subject}." + (" Use the attached image as the composition reference." if has_reference else "")
    )
    panel_lines = "\n".join(f"  Cell {s.stage}: {s.prompt}" for s in stages)
    blank = f"\n  Cells {len(stages) + 1}-{cells}: leave completely blank (plain white)." if cells > len(stages) else ""

    return f"""Create a single step-by-step tutorial sheet: a {rows} x {cols} grid of equal square cells,
read left-to-right, top-to-bottom. Style: {MODE_STYLE[mode]}.
{subject_line}

ABSOLUTE RULES:
- Every cell shows the SAME drawing at the SAME position, scale and framing (pixel-registered),
  as if photographing one canvas at successive moments.
- Each cell is a strict continuation of the previous cell: it contains EVERYTHING from the
  previous cell unchanged, plus only the new marks for that stage. Never erase, move or redraw.
- No text, numbers, labels, borders or gutters. Plain background.

{panel_lines}{blank}
"""


class GeminiService:
    def __init__(self) -> None:
        self._client = None
        if settings.GEMINI_API_KEY:
            try:
                from google import genai

                self._client = genai.Client(api_key=settings.GEMINI_API_KEY)
            except Exception as exc:  # pragma: no cover - depends on env
                logger.warning("Gemini client init failed: %s", exc)

    @property
    def available(self) -> bool:
        return self._client is not None

    def generate_stage_sheet(self, mode: str, subject: str | None, reference: Image.Image | None) -> Image.Image:
        if not self._client:
            raise GeminiUnavailable("GEMINI_API_KEY is not configured")

        from google.genai import types

        rows, cols = settings.SHEET_ROWS, settings.SHEET_COLS
        prompt = build_sheet_prompt(mode, subject, reference is not None, rows, cols)
        contents: list = [prompt]
        if reference is not None:
            contents.append(reference)

        try:
            response = self._client.models.generate_content(
                model=settings.GEMINI_IMAGE_MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    response_modalities=["IMAGE"],
                    image_config=types.ImageConfig(aspect_ratio=f"{cols}:{rows}"),
                ),
            )
        except Exception as exc:
            raise GeminiUnavailable(f"Gemini request failed: {exc}") from exc

        for part in response.parts or []:
            if part.inline_data and part.inline_data.data:
                return Image.open(io.BytesIO(part.inline_data.data)).convert("RGB")
        raise GeminiUnavailable("Gemini returned no image (possibly blocked by safety filters)")


_service: GeminiService | None = None


def get_gemini_service() -> GeminiService:
    global _service
    if _service is None:
        _service = GeminiService()
    return _service
