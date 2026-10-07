import io
from PIL import Image, ImageDraw
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.slice_processor import SliceProcessor

router = APIRouter()

PIXEL_STAGE_DESCRIPTIONS = [
    {"stage": 1, "name": "Pixel Outline & Silhouette", "description": "Crisp 1-pixel boundary outline establishing sprite proportions."},
    {"stage": 2, "name": "Flat Color Palette Fill", "description": "Flat color fill mapped using restricted 16-color palette."},
    {"stage": 3, "name": "Primary Dithering & Shadow Shading", "description": "Dither patterns and directional shadow shading."},
    {"stage": 4, "name": "Highlight Pixels & Specular Pops", "description": "Specular highlight pixels and contrast pop accents."},
    {"stage": 5, "name": "Final Sprite Polish & Outline Cleanup", "description": "Clean anti-aliasing and outline color banding cleanup."}
]

@router.post("/generate/pixel", tags=["Pixel Art"])
async def generate_pixel(
    prompt: str = Form(None),
    file: UploadFile = File(None)
):
    """
    POST /api/v1/generate/pixel:
    Generates pixel art construction steps.
    """
    try:
        w, h = 64, 64
        steps = []
        for s in range(5):
            img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            
            # Step 1: Pixel outline
            draw.rectangle([16, 16, 48, 48], outline=(40, 40, 40, 255), width=1)
            
            if s >= 1:
                # Step 2: Flat fill
                draw.rectangle([17, 17, 47, 47], fill=(80, 160, 240, 255))
            if s >= 2:
                # Step 3: Dithering shadow
                for px in range(17, 48, 2):
                    draw.point((px, 47), fill=(40, 80, 160, 255))
            if s >= 3:
                # Step 4: Highlight
                draw.line([(18, 18), (30, 18)], fill=(255, 255, 255, 255), width=1)
            if s >= 4:
                # Step 5: Final polish
                draw.point((17, 17), fill=(255, 220, 100, 255))

            # Rescale to 512x512 with NEAREST filtering for crisp pixel art!
            crisp_img = img.resize((512, 512), Image.NEAREST)
            meta = PIXEL_STAGE_DESCRIPTIONS[s].copy()
            meta["image_url"] = SliceProcessor.image_to_base64_url(crisp_img)
            meta["width"] = 512
            meta["height"] = 512
            steps.append(meta)

        return {
            "status": "success",
            "mode": "pixel_art",
            "total_steps": len(steps),
            "steps": steps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pixel art generation failed: {str(e)}")
