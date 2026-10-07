import cv2
import numpy as np
from PIL import Image, ImageDraw
from app.services.layering import LayerStack, verify_stack
from app.services.slice_processor import SliceProcessor
from app.services.stages import SKETCH_STAGES

class SketchEngine:
    """
    Cumulative Sketching Decomposition Engine.
    Ensures every stage is a STRICT VISUAL CONTINUATION of the preceding stage.
    Uses LayerStack so Stage K is mathematically: Composite_{K-1} + Layer_K.
    """

    @staticmethod
    def decompose_image_to_sketch_stack(input_image: Image.Image) -> tuple[LayerStack, list[dict]]:
        """
        Decomposes an input reference image into 5 cumulative sketching stages.
        """
        cv_img = cv2.cvtColor(np.array(input_image.convert("RGB")), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # White background canvas
        bg = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        stack = LayerStack(background=bg)

        # Stage 1: Gesture & Basic Scaffolding (Light cyan scaffolding lines)
        layer1_arr = np.zeros((h, w, 4), dtype=np.uint8)
        cv2.line(layer1_arr, (w // 2, 0), (w // 2, h), (180, 200, 230, 160), 1, cv2.LINE_AA)
        cv2.line(layer1_arr, (0, h // 2), (w, h // 2), (180, 200, 230, 160), 1, cv2.LINE_AA)
        cv2.rectangle(layer1_arr, (w // 6, h // 6), (5 * w // 6, 5 * h // 6), (180, 200, 230, 120), 1, cv2.LINE_AA)
        
        blurred = cv2.GaussianBlur(gray, (9, 9), 0)
        contours, _ = cv2.findContours(cv2.Canny(blurred, 30, 100), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if cv2.contourArea(c) > (w * h * 0.03):
                ellipse = cv2.fitEllipse(c) if len(c) >= 5 else None
                if ellipse:
                    cv2.ellipse(layer1_arr, ellipse, (160, 190, 220, 160), 1, cv2.LINE_AA)
        
        layer1_pil = Image.fromarray(layer1_arr, mode="RGBA")
        stack.push(layer1_pil)

        # Stage 2: Primary Silhouette / Block-In (Graphite contours)
        layer2_arr = np.zeros((h, w, 4), dtype=np.uint8)
        canny_contour = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(canny_contour, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        for c in contours:
            if cv2.contourArea(c) > (w * h * 0.005):
                cv2.drawContours(layer2_arr, [c], -1, (60, 60, 70, 220), 1, cv2.LINE_AA)
        
        layer2_pil = Image.fromarray(layer2_arr, mode="RGBA")
        stack.push(layer2_pil)

        # Stage 3: Secondary Features & Plane Breaks
        layer3_arr = np.zeros((h, w, 4), dtype=np.uint8)
        detail_lines = cv2.Canny(gray, 80, 180)
        y_indices, x_indices = np.where(detail_lines > 0)
        layer3_arr[y_indices, x_indices] = [40, 40, 50, 230]
        layer3_pil = Image.fromarray(layer3_arr, mode="RGBA")
        stack.push(layer3_pil)

        # Stage 4: Value & Cross-Hatching
        layer4_arr = np.zeros((h, w, 4), dtype=np.uint8)
        dark_regions = gray < 120
        hatch_mask = np.zeros((h, w), dtype=np.uint8)
        for y in range(0, h, 6):
            for x in range(0, w, 6):
                if dark_regions[y, x]:
                    cv2.line(hatch_mask, (x, y), (min(x + 4, w - 1), min(y + 4, h - 1)), 255, 1)
        hatch_y, hatch_x = np.where(hatch_mask > 0)
        layer4_arr[hatch_y, hatch_x] = [30, 30, 40, 180]
        layer4_pil = Image.fromarray(layer4_arr, mode="RGBA")
        stack.push(layer4_pil)

        # Stage 5: Line Weight Accents & Fine Details
        layer5_arr = np.zeros((h, w, 4), dtype=np.uint8)
        thick_edges = cv2.Canny(gray, 120, 220)
        kernel = np.ones((2, 2), np.uint8)
        thick_edges = cv2.dilate(thick_edges, kernel, iterations=1)
        accent_y, accent_x = np.where(thick_edges > 0)
        layer5_arr[accent_y, accent_x] = [15, 15, 20, 255]
        layer5_pil = Image.fromarray(layer5_arr, mode="RGBA")
        stack.push(layer5_pil)

        # Verify continuity mathematically
        report = verify_stack(stack)

        # Formulate API response payload
        step_payloads = []
        for idx, stage_layer in enumerate(stack.stages):
            spec = SKETCH_STAGES[idx]
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
    def generate_synthetic_sketch(prompt: str) -> tuple[LayerStack, list[dict]]:
        """
        Creates clean 5-stage progressive sketch vector layers for synthetic prompt mode.
        """
        w, h = 512, 512
        bg = Image.new("RGBA", (w, h), (255, 255, 255, 255))
        stack = LayerStack(background=bg)

        # Stage 1: Scaffolding
        l1 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d1 = ImageDraw.Draw(l1)
        d1.line([(w // 4, h // 4), (3 * w // 4, 3 * h // 4)], fill=(180, 200, 230, 180), width=2)
        d1.line([(3 * w // 4, h // 4), (w // 4, 3 * h // 4)], fill=(180, 200, 230, 180), width=2)
        d1.ellipse([w // 4, h // 4, 3 * w // 4, 3 * h // 4], outline=(170, 195, 225, 180), width=2)
        stack.push(l1)

        # Stage 2: Outline
        l2 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d2 = ImageDraw.Draw(l2)
        d2.rectangle([w // 4 + 20, h // 4 + 20, 3 * w // 4 - 20, 3 * h // 4 - 20], outline=(60, 60, 70, 220), width=3)
        d2.ellipse([w // 4 + 40, h // 4 + 40, 3 * w // 4 - 40, 3 * h // 4 - 40], outline=(60, 60, 70, 220), width=3)
        stack.push(l2)

        # Stage 3: Features
        l3 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d3 = ImageDraw.Draw(l3)
        d3.line([(w // 2, h // 4 + 40), (w // 2, 3 * h // 4 - 40)], fill=(40, 40, 50, 230), width=2)
        d3.line([(w // 4 + 40, h // 2), (3 * w // 4 - 40, h // 2)], fill=(40, 40, 50, 230), width=2)
        stack.push(l3)

        # Stage 4: Hatching
        l4 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d4 = ImageDraw.Draw(l4)
        for y in range(h // 4 + 50, 3 * h // 4 - 50, 12):
            d4.line([(w // 4 + 50, y), (w // 2, y + 10)], fill=(30, 30, 40, 160), width=1)
        stack.push(l4)

        # Stage 5: Accents
        l5 = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        d5 = ImageDraw.Draw(l5)
        d5.rectangle([w // 4 + 18, h // 4 + 18, 3 * w // 4 - 18, 3 * h // 4 - 18], outline=(15, 15, 20, 255), width=4)
        stack.push(l5)

        step_payloads = []
        for idx, stage_layer in enumerate(stack.stages):
            spec = SKETCH_STAGES[idx]
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
