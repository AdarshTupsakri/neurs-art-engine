import pytest
from PIL import Image
from app.services.paint_engine import PaintEngine

def test_paint_synthetic_stages():
    """Verifies painterly synthetic layer generation yields 5 structured steps."""
    steps = PaintEngine.generate_synthetic_paint("Landscape Atelier Study")
    assert len(steps) == 5
    for idx, step in enumerate(steps):
        assert step["stage"] == idx + 1
        assert "Imprimatura" in steps[0]["name"] or "Wash" in steps[0]["name"] or "Monochromatic" in steps[0]["technique"]
        assert "Highlights" in steps[4]["name"]

def test_paint_image_decomposition_stages():
    """Verifies image decomposition for painterly pipeline."""
    test_img = Image.new("RGB", (100, 100), (200, 150, 100))
    steps = PaintEngine.generate_cumulative_paint_from_image(test_img)
    assert len(steps) == 5
    for step in steps:
        assert step["width"] == 100
        assert step["height"] == 100
        assert step["image_url"].startswith("data:image/png;base64,")
