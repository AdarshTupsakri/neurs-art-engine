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
        Decomposes an input reference image into 5 progressive, beginner-friendly sketching stages.
        Stage 1: Proportional Scaffolding (Grid & primary bounding shapes)
        Stage 2: Outer Silhouette Block-In (Simplified outer contour)
        Stage 3: Internal Seams & Feature Landmarks (Major internal division lines)
        Stage 4: Value & Form Shading (45-degree directional cross-hatching)
        Stage 5: Line Weight Accents & Fine Details (Sharp dark accents)
        """
        cv_img = cv2.cvtColor(np.array(input_image.convert("RGB")), cv2.COLOR_RGB2BGR)
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        h, w = gray.shape

        # Clean off-white paper canvas background
        bg = Image.new("RGBA", (w, h), (250, 248, 245, 255))
        stack = LayerStack(background=bg)

        # -------------------------------------------------------------------
        # Stage 1: Proportional Scaffolding & Axis Lines
        # -------------------------------------------------------------------
        layer1_arr = np.zeros((h, w, 4), dtype=np.uint8)
        
        # Rule of thirds & center crosshairs in light cyan
        cyan_light = (200, 220, 240, 160)
        cv2.line(layer1_arr, (w // 2, 0), (w // 2, h), cyan_light, 1, cv2.LINE_AA)
        cv2.line(layer1_arr, (0, h // 2), (w, h // 2), cyan_light, 1, cv2.LINE_AA)
        cv2.line(layer1_arr, (w // 3, 0), (w // 3, h), cyan_light, 1, cv2.LINE_AA)
        cv2.line(layer1_arr, (2 * w // 3, 0), (2 * w // 3, h), cyan_light, 1, cv2.LINE_AA)
        cv2.line(layer1_arr, (0, h // 3), (w, h // 3), cyan_light, 1, cv2.LINE_AA)
        cv2.line(layer1_arr, (0, 2 * h // 3), (w, 2 * h // 3), cyan_light, 1, cv2.LINE_AA)

        # Primary outer bounding box & primary fitted mass ellipse ONLY
        blurred_heavy = cv2.GaussianBlur(gray, (25, 25), 0)
        _, thresh_outer = cv2.threshold(blurred_heavy, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        contours_ext, _ = cv2.findContours(thresh_outer, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours_ext:
            largest_c = max(contours_ext, key=cv2.contourArea)
            if cv2.contourArea(largest_c) > (w * h * 0.02):
                x, y, bw, bh = cv2.boundingRect(largest_c)
                cv2.rectangle(layer1_arr, (x, y), (x + bw, y + bh), cyan_light, 1, cv2.LINE_AA)
                if len(largest_c) >= 5:
                    ellipse = cv2.fitEllipse(largest_c)
                    cv2.ellipse(layer1_arr, ellipse, (170, 200, 235, 180), 2, cv2.LINE_AA)
        
        stack.push(Image.fromarray(layer1_arr, mode="RGBA"))

        # -------------------------------------------------------------------
        # Stage 2: Simplified Outer Silhouette Outline (Outer Block-In)
        # -------------------------------------------------------------------
        layer2_arr = np.zeros((h, w, 4), dtype=np.uint8)
        canny_outer = cv2.Canny(blurred_heavy, 30, 90)
        contours_outer, _ = cv2.findContours(canny_outer, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for c in contours_outer:
            if cv2.contourArea(c) > (w * h * 0.005) or cv2.arcLength(c, False) > (w * 0.2):
                # Smooth the contour to remove small bumps for beginner outline tracing
                epsilon = 0.008 * cv2.arcLength(c, True)
                approx = cv2.approxPolyDP(c, epsilon, True)
                cv2.drawContours(layer2_arr, [approx], -1, (50, 50, 65, 240), 2, cv2.LINE_AA)
        
        stack.push(Image.fromarray(layer2_arr, mode="RGBA"))

        # -------------------------------------------------------------------
        # Stage 3: Major Internal Seams & Feature Landmarks
        # -------------------------------------------------------------------
        layer3_arr = np.zeros((h, w, 4), dtype=np.uint8)
        blurred_mid = cv2.GaussianBlur(gray, (9, 9), 0)
        canny_internal = cv2.Canny(blurred_mid, 50, 130)
        contours_mid, hierarchy = cv2.findContours(canny_internal, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for idx, c in enumerate(contours_mid):
            arc_len = cv2.arcLength(c, False)
            if arc_len > (w * 0.05):
                # Draw internal structural division lines
                cv2.drawContours(layer3_arr, [c], -1, (40, 40, 50, 220), 1, cv2.LINE_AA)
        
        stack.push(Image.fromarray(layer3_arr, mode="RGBA"))

        # -------------------------------------------------------------------
        # Stage 4: Form Shading & 45-Degree Cross-Hatching
        # -------------------------------------------------------------------
        layer4_arr = np.zeros((h, w, 4), dtype=np.uint8)
        dark_mask = gray < 110
        hatch_spacing = 8
        
        for y in range(0, h, hatch_spacing):
            for x in range(0, w, hatch_spacing):
                if dark_mask[y, x]:
                    x2 = min(x + 6, w - 1)
                    y2 = min(y + 6, h - 1)
                    cv2.line(layer4_arr, (x, y), (x2, y2), (30, 30, 45, 170), 1, cv2.LINE_AA)
        
        stack.push(Image.fromarray(layer4_arr, mode="RGBA"))

        # -------------------------------------------------------------------
        # Stage 5: Line Weight Accents & Fine Details
        # -------------------------------------------------------------------
        layer5_arr = np.zeros((h, w, 4), dtype=np.uint8)
        detail_edges = cv2.Canny(gray, 90, 190)
        kernel = np.ones((2, 2), np.uint8)
        accent_edges = cv2.dilate(detail_edges, kernel, iterations=1)
        
        y_acc, x_acc = np.where(accent_edges > 0)
        layer5_arr[y_acc, x_acc] = [15, 15, 22, 255]
        
        stack.push(Image.fromarray(layer5_arr, mode="RGBA"))

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
