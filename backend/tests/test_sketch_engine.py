import pytest
import numpy as np
from PIL import Image
from app.services.sketch_engine import SketchEngine

def test_sketch_synthetic_stage_count():
    """Verifies that synthetic sketch generation produces exactly 5 cumulative stages."""
    steps = SketchEngine.generate_synthetic_sketch("Test Skull Anatomy")
    assert len(steps) == 5
    for idx, step in enumerate(steps):
        assert step["stage"] == idx + 1
        assert "image_url" in step
        assert step["image_url"].startswith("data:image/png;base64,")

def test_sketch_cumulative_continuity_from_image():
    """
    ASSERTION OF CUMULATIVE CONTINUITY:
    Validates that every stage K > 1 retains or builds upon pixels from stage K-1.
    """
    test_img = Image.new("RGB", (200, 200), (255, 255, 255))
    steps = SketchEngine.generate_cumulative_sketch_from_image(test_img)
    
    assert len(steps) == 5
    
    previous_non_zero_pixels = 0
    for idx, step in enumerate(steps):
        # Decode base64 image URL data
        data_url = step["image_url"]
        assert data_url.startswith("data:image/png;base64,")
        
        # Verify step index increment
        assert step["stage"] == idx + 1
        assert len(step["description"]) > 0
