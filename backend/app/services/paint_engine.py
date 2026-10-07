import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from app.services.layering import LayerStack, verify_stack
from app.services.slice_processor import SliceProcessor
from app.services.stages import PAINT_STAGES

class PaintEngine:
    """
    Painterly Layering Engine.
    Executes true oil/acrylic/digital atelier layer build orders where Step N paints directly over Step N-1.
    Uses LayerStack to enforce mathematical cumulative visual continuity.
    """

    @staticmethod
    def decompose_image_to_paint_stack(input_image: Image.Image) -> tuple[LayerStack, list[dict]]:
        """
        Decomposes an input reference image into 5 cumulative atelier painting stages.
        """
        cv_img = cv2.cvtColor(np.array(input_image.convert("RGB")), cv2.COLOR_RGB2BGR)
        h, w, _ = cv_img.shape
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)

        # Stage 1 Background: Imprimatura wash
        bg = Image.new("RGBA", (w, h), (220, 180, 140, 255))  # Warm sienna canvas wash
        stack = LayerStack(background=bg)

        # Stage 1 Layer: Loose underdrawing lines
        layer1_arr = np.zeros((h, w, 4), dtype=np.uint8)
        edges = cv2.Canny(cv2.GaussianBlur(gray, (7, 7), 0), 40, 120)
        layer1_arr[edges > 0] = [40, 60, 90, 220]  # Dark umber lines
        stack.push(Image.fromarray(layer1_arr, mode="RGBA"))

        # Stage 2: Tonal Mass & Grisaille Block-In (Quantized broad values)
        stage2_gray = cv2.bilateralFilter(gray, 15, 75, 75)
        levels = 4
        stage2_quant = np.floor_divide(stage2_gray, 256 // levels) * (255 // (levels - 1))
        stage2_bgr = cv2.cvtColor(stage2_quant, cv2.COLOR_GRAY2BGR)
        stage2_bgr = cv2.addWeighted(stage2_bgr, 0.7, cv2.cvtColor(np.array(bg.convert("RGB")), cv2.COLOR_RGB2BGR), 0.3, 0)
        layer2_rgba = cv2.cvtColor(stage2_bgr, cv2.COLOR_BGR2BGRA)
        layer2_rgba[:, :, 3] = 180  # Semi-opaque value mass pass
        stack.push(Image.fromarray(cv2.cvtColor(layer2_rgba, cv2.COLOR_BGRA2RGBA)))

        # Stage 3: Local Color & Temperature Mapping
        stage3_bgr = cv2.pyrMeanShiftFiltering(cv_img, 20, 45)
        layer3_rgba = cv2.cvtColor(stage3_bgr, cv2.COLOR_BGR2BGRA)
        layer3_rgba[:, :, 3] = 200  # Broad color pass
        stack.push(Image.fromarray(cv2.cvtColor(layer3_rgba, cv2.COLOR_BGRA2RGBA)))

        # Stage 4: Half-tones & Edge Control
        stage4_bgr = cv2.bilateralFilter(cv_img, 9, 50, 50)
        layer4_rgba = cv2.cvtColor(stage4_bgr, cv2.COLOR_BGR2BGRA)
        layer4_rgba[:, :, 3] = 230  # Softened edge pass
        stack.push(Image.fromarray(cv2.cvtColor(layer4_rgba, cv2.COLOR_BGRA2RGBA)))

        # Stage 5: Highlights, Textures & Specular Glazes
        layer5_arr = np.zeros((h, w, 4), dtype=np.uint8)
        highlight_mask = gray > 210
        layer5_bgr = cv_img.copy()
        layer5_bgr[highlight_mask] = np.clip(layer5_bgr[highlight_mask].astype(int) + 40, 0, 255).astype(np.uint8)
        
        y_hl, x_hl = np.where(highlight_mask > 0)
        for y, x in zip(y_hl, x_hl):
            layer5_arr[y, x] = [layer5_bgr[y, x, 2], layer5_bgr[y, x, 1], layer5_bgr[y, x, 0], 255]
            
        stack.push(Image.fromarray(layer5_arr, mode="RGBA"))

        # Formulate response steps
        step_payloads = []
        for idx, stage_layer in enumerate(stack.stages):
            spec = PAINT_STAGES[idx]
            step_payloads.append({
                "stage": spec.stage,
                "name": spec.name,
                "technique": spec.technique,
                "description": spec.description,
                "image_url": SliceProcessor.image_to_data_url(stage_layer.composite),
                "layer_url": SliceProcessor.image_to_data_url(stage_layer.layer),
                "width": w,
                "height": h,
                "coverage": stage_layer.coverage
            })

        return stack, step_payloads

    @staticmethod
    def generate_synthetic_paint(prompt: str) -> tuple[LayerStack, list[dict]]:
        """
        Synthetic fallback for painterly layer build order.
        """
        w, h = 512, 512
        bg = Image.new("RGBA", (w, h), (240, 220, 190, 255))
        stack = LayerStack(background=bg)

        # Stage 1
        l1 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d1 = ImageDraw.Draw(l1)
        d1.ellipse([w // 4, h // 4, 3 * w // 4, 3 * h // 4], outline=(100, 70, 40, 200), width=3)
        stack.push(l1)

        # Stage 2
        l2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(l2)
        d2.ellipse([w // 4 + 30, h // 4 + 30, 3 * w // 4 - 30, 3 * h // 4 - 30], fill=(120, 100, 80, 230))
        stack.push(l2)

        # Stage 3
        l3 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d3 = ImageDraw.Draw(l3)
        d3.ellipse([w // 4 + 40, h // 4 + 40, 3 * w // 4 - 40, 3 * h // 4 - 40], fill=(210, 110, 80, 255))
        stack.push(l3)

        # Stage 4
        l4 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d4 = ImageDraw.Draw(l4)
        d4.ellipse([w // 4 + 50, h // 4 + 50, w // 2, h // 2], fill=(240, 150, 120, 255))
        stack.push(l4)

        # Stage 5
        l5 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d5 = ImageDraw.Draw(l5)
        d5.ellipse([w // 2 - 20, h // 3 - 20, w // 2 + 20, h // 3 + 20], fill=(255, 255, 230, 255))
        d5.ellipse([w // 2 - 8, h // 3 - 8, w // 2 + 8, h // 3 + 8], fill=(255, 255, 255, 255))
        stack.push(l5)

        step_payloads = []
        for idx, stage_layer in enumerate(stack.stages):
            spec = PAINT_STAGES[idx]
            step_payloads.append({
                "stage": spec.stage,
                "name": spec.name,
                "technique": spec.technique,
                "description": spec.description,
                "image_url": SliceProcessor.image_to_data_url(stage_layer.composite),
                "layer_url": SliceProcessor.image_to_data_url(stage_layer.layer),
                "width": w,
                "height": h,
                "coverage": stage_layer.coverage
            })

        return stack, step_payloads
