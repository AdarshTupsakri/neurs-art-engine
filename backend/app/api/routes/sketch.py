from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.core.security import read_upload_image
from app.services.sketch_engine import SketchEngine

router = APIRouter()

@router.post("/generate/sketch", tags=["Sketching"])
async def generate_sketch(
    prompt: str = Form(None),
    file: UploadFile = File(None)
):
    """
    POST /api/v1/generate/sketch:
    Decomposes prompt or uploaded image into 5 cumulative sketching stages.
    """
    try:
        if file and file.filename:
            input_image = await read_upload_image(file)
            _, steps = SketchEngine.decompose_image_to_sketch_stack(input_image)
            mode_used = "image_decomposition"
        else:
            target_prompt = prompt or "Classic Human Face Anatomy"
            _, steps = SketchEngine.generate_synthetic_sketch(target_prompt)
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
        raise HTTPException(status_code=500, detail=f"Sketch decomposition failed: {str(e)}")
