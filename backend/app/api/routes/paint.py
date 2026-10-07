from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.core.security import read_upload_image
from app.services.paint_engine import PaintEngine

router = APIRouter()

@router.post("/generate/paint", tags=["Painting"])
async def generate_paint(
    prompt: str = Form(None),
    file: UploadFile = File(None)
):
    """
    POST /api/v1/generate/paint:
    Decomposes prompt or uploaded image into 5 cumulative atelier painterly stages.
    """
    try:
        if file and file.filename:
            input_image = await read_upload_image(file)
            _, steps = PaintEngine.decompose_image_to_paint_stack(input_image)
            mode_used = "image_decomposition"
        else:
            target_prompt = prompt or "Classic Atelier Oil Painting"
            _, steps = PaintEngine.generate_synthetic_paint(target_prompt)
            mode_used = "prompt_decomposition"

        return {
            "status": "success",
            "mode": mode_used,
            "total_steps": len(steps),
            "steps": steps
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Painterly layer decomposition failed: {str(e)}")
