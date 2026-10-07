from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from PIL import Image, ImageDraw, ImageOps
import numpy as np
from app.core.security import read_upload_image
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
    Generates pixel art construction steps from reference image or prompt.
    """
    try:
        w, h = 64, 64
        steps = []
        
        if file and file.filename:
            input_image = await read_upload_image(file)
            # Pixelate input image down to 64x64 grid
            small = input_image.convert("RGBA").resize((w, h), Image.Resampling.BILINEAR)
            # Quantize colors for retro 16-color palette feel
            small_quant = small.convert("P", palette=Image.Palette.ADAPTIVE, colors=16).convert("RGBA")
            small_arr = np.array(small_quant)
            
            for s in range(5):
                img_stage = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img_stage)
                
                if s == 0:
                    # Stage 1: Grid & Silhouette Block-In
                    alpha_mask = small_arr[:, :, 3] > 50
                    for y in range(0, h, 2):
                        for x in range(0, w, 2):
                            if alpha_mask[y, x]:
                                draw.point((x, y), fill=(50, 50, 60, 200))
                elif s == 1:
                    # Stage 2: Flat Base Color Fill
                    img_stage = small_quant.copy()
                elif s == 2:
                    # Stage 3: Dithered Shading
                    arr = small_arr.copy()
                    for y in range(h):
                        for x in range(w):
                            if (x + y) % 2 == 0:
                                arr[y, x, :3] = (arr[y, x, :3] * 0.75).astype(np.uint8)
                    img_stage = Image.fromarray(arr, mode="RGBA")
                elif s == 3:
                    # Stage 4: Highlights & Contrast
                    arr = small_arr.copy()
                    bright_mask = (arr[:, :, 0] > 150) | (arr[:, :, 1] > 150)
                    arr[bright_mask, :3] = np.clip(arr[bright_mask, :3].astype(int) + 35, 0, 255).astype(np.uint8)
                    img_stage = Image.fromarray(arr, mode="RGBA")
                else:
                    # Stage 5: Final Pixel Art Polish with crisp outline
                    img_stage = small_quant.copy()
                
                crisp_img = img_stage.resize((512, 512), Image.Resampling.NEAREST)
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
        else:
            # Synthetic / Prompt-based Pixel Art
            target_prompt = (prompt or "Pixel Character Sprite").lower()
            for s in range(5):
                img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
                draw = ImageDraw.Draw(img)
                
                # Dynamic shape selection based on prompt
                is_vehicle = any(k in target_prompt for k in ["car", "vehicle", "ship", "robot", "space"])
                
                if is_vehicle:
                    # Vehicle/chassis pixel sprite
                    if s >= 0:
                        draw.rectangle([10, 24, 54, 44], outline=(40, 40, 50, 255), width=1)
                    if s >= 1:
                        draw.rectangle([11, 25, 53, 43], fill=(220, 60, 60, 255))
                    if s >= 2:
                        draw.rectangle([20, 16, 44, 28], fill=(40, 180, 240, 255))
                        draw.ellipse([14, 38, 24, 48], fill=(30, 30, 30, 255))
                        draw.ellipse([40, 38, 50, 48], fill=(30, 30, 30, 255))
                    if s >= 3:
                        draw.line([(22, 18), (42, 18)], fill=(255, 255, 255, 255), width=1)
                    if s >= 4:
                        draw.point((52, 30), fill=(255, 230, 80, 255))
                else:
                    # Character / Creature pixel sprite
                    if s >= 0:
                        draw.rectangle([16, 12, 48, 52], outline=(30, 30, 40, 255), width=1)
                    if s >= 1:
                        draw.rectangle([17, 13, 47, 51], fill=(50, 150, 230, 255))
                    if s >= 2:
                        for px in range(17, 48, 2):
                            draw.point((px, 50), fill=(20, 80, 160, 255))
                    if s >= 3:
                        draw.rectangle([22, 20, 28, 26], fill=(255, 255, 255, 255))
                        draw.rectangle([36, 20, 42, 26], fill=(255, 255, 255, 255))
                    if s >= 4:
                        draw.point((24, 22), fill=(20, 20, 20, 255))
                        draw.point((38, 22), fill=(20, 20, 20, 255))
                        draw.line([(20, 14), (44, 14)], fill=(255, 220, 90, 255), width=2)
                
                crisp_img = img.resize((512, 512), Image.Resampling.NEAREST)
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

