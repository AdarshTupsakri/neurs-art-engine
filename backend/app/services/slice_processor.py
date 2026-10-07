"""
Deterministic sheet slicing + registration.

Gemini returns ONE sheet containing every construction stage (one call = no style drift,
1/N the cost). This module turns that sheet into N pixel-registered frames:

1. slice_grid      - split the sheet into equal cells (row-major reading order)
2. trim_gutters    - shave the uniform border/gutter the model tends to draw round cells
3. normalize_sizes - resample every frame to one common size
4. register_frames - estimate each frame's translation against the FINAL frame
                     (phase correlation) and undo it, so stage k sits exactly on k-1
"""
from __future__ import annotations

import base64
import io
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image


@dataclass
class RegistrationReport:
    offsets: list[tuple[float, float]]  # (dx, dy) correction applied to each frame
    max_shift_px: float
    aligned: bool  # False if any shift exceeded the sanity limit (frame left untouched)


class SliceProcessor:
    # A drift larger than this fraction of the frame is treated as a different composition,
    # not a registration error, and is NOT "corrected" (that would smear the image).
    MAX_SHIFT_FRACTION = 0.08

    # ----------------------------------------------------------------- slicing
    @staticmethod
    def slice_grid(sheet: Image.Image, rows: int, cols: int, count: int | None = None) -> list[Image.Image]:
        width, height = sheet.size
        cell_w, cell_h = width // cols, height // rows
        frames: list[Image.Image] = []
        for r in range(rows):
            for c in range(cols):
                frames.append(sheet.crop((c * cell_w, r * cell_h, (c + 1) * cell_w, (r + 1) * cell_h)))
        return frames[: count or len(frames)]

    @staticmethod
    def trim_gutters(frame: Image.Image, tolerance: int = 12, max_trim_fraction: float = 0.06) -> Image.Image:
        """Crop a uniform-coloured border (gutter / frame line) from every side, symmetrically."""
        arr = np.asarray(frame.convert("RGB")).astype(np.int16)
        h, w, _ = arr.shape
        border_color = np.median(np.concatenate([arr[0], arr[-1], arr[:, 0], arr[:, -1]]), axis=0)
        max_trim = int(min(h, w) * max_trim_fraction)

        def uniform(line: np.ndarray) -> bool:
            return bool(np.all(np.abs(line - border_color).max(axis=-1) <= tolerance))

        trim = 0
        while trim < max_trim and all(
            uniform(x) for x in (arr[trim], arr[h - 1 - trim], arr[:, trim], arr[:, w - 1 - trim])
        ):
            trim += 1
        if trim == 0:
            return frame
        return frame.crop((trim, trim, w - trim, h - trim))

    @staticmethod
    def normalize_sizes(frames: list[Image.Image], size: tuple[int, int] | None = None) -> list[Image.Image]:
        if not frames:
            return frames
        target = size or min((f.size for f in frames), key=lambda s: s[0] * s[1])
        return [f if f.size == target else f.resize(target, Image.LANCZOS) for f in frames]

    # ------------------------------------------------------------ registration
    @classmethod
    def register_frames(cls, frames: list[Image.Image]) -> tuple[list[Image.Image], RegistrationReport]:
        """Align every frame to the last (most complete) frame by pure translation."""
        if len(frames) < 2:
            return frames, RegistrationReport([(0.0, 0.0)] * len(frames), 0.0, True)

        def edges(img: Image.Image) -> np.ndarray:
            # Correlate on edge maps: robust to the large value/colour changes between stages.
            gray = cv2.cvtColor(np.asarray(img.convert("RGB")), cv2.COLOR_RGB2GRAY)
            e = cv2.Canny(cv2.GaussianBlur(gray, (5, 5), 0), 40, 120).astype(np.float32)
            return cv2.GaussianBlur(e, (9, 9), 0)

        ref = edges(frames[-1])
        h, w = ref.shape
        window = cv2.createHanningWindow((w, h), cv2.CV_32F)
        limit = cls.MAX_SHIFT_FRACTION * min(w, h)

        aligned, offsets, all_ok = [], [], True
        for frame in frames:
            (dx, dy), response = cv2.phaseCorrelate(ref, edges(frame), window)
            shift = float(np.hypot(dx, dy))
            if shift < 0.5 or response < 0.05:
                aligned.append(frame)
                offsets.append((0.0, 0.0))
                continue
            if shift > limit:
                all_ok = False
                aligned.append(frame)
                offsets.append((0.0, 0.0))
                continue
            matrix = np.float32([[1, 0, -dx], [0, 1, -dy]])
            arr = np.asarray(frame.convert("RGB"))
            border = tuple(int(v) for v in np.median(arr.reshape(-1, 3), axis=0))
            moved = cv2.warpAffine(arr, matrix, (w, h), flags=cv2.INTER_LINEAR,
                                   borderMode=cv2.BORDER_CONSTANT, borderValue=border)
            aligned.append(Image.fromarray(moved))
            offsets.append((-float(dx), -float(dy)))

        max_shift = max(float(np.hypot(*o)) for o in offsets)
        return aligned, RegistrationReport(offsets, max_shift, all_ok)

    # --------------------------------------------------------------- pipeline
    @classmethod
    def sheet_to_frames(
        cls, sheet: Image.Image, rows: int, cols: int, count: int
    ) -> tuple[list[Image.Image], RegistrationReport]:
        frames = [cls.trim_gutters(f) for f in cls.slice_grid(sheet.convert("RGB"), rows, cols, count)]
        frames = cls.normalize_sizes(frames)
        return cls.register_frames(frames)

    # ------------------------------------------------------------- encoding
    @staticmethod
    def image_to_data_url(image: Image.Image) -> str:
        buf = io.BytesIO()
        image.save(buf, format="PNG", optimize=True)
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")

    @staticmethod
    def data_url_to_image(url: str) -> Image.Image:
        _, b64 = url.split(",", 1)
        return Image.open(io.BytesIO(base64.b64decode(b64)))
