from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from PIL import Image, ImageDraw
from app.services.slice_processor import SliceProcessor
from app.services.stages import PIXEL_STAGES

router = APIRouter()

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

            crisp_img = img.resize((512, 512), Image.NEAREST)
            spec = PIXEL_STAGES[s]
            steps.append({
                "stage": spec.stage,
                "name": spec.name,
                "technique": spec.technique,
                "description": spec.description,
                "image_url": SliceProcessor.image_to_data_url(crisp_img),
                "width": 512,
                "height": 512
            })

        return {
            "status": "success",
            "mode": "pixel_art",
            "total_steps": len(steps),
            "steps": steps
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pixel art generation failed: {str(e)}")
