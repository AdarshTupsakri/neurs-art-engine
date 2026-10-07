"""
Stage definitions for every mode. Single source of truth for:
  - the Gemini sheet prompt (what each panel must contain)
  - the per-step explanation text returned to the frontend
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class StageSpec:
    stage: int
    name: str
    technique: str
    description: str  # learner-facing explanation
    prompt: str       # what the model must ADD in this panel


SKETCH_STAGES: list[StageSpec] = [
    StageSpec(1, "Gesture & Basic Forms", "Scaffolding",
              "Loose bounding box, centre-of-gravity and symmetry axes, perspective lines, and the primary "
              "masses (circles, ovals, cylinders, boxes). Keep everything light - these are guides, not outlines.",
              "very light, thin blue-grey construction lines only: bounding box, centre and symmetry axes, "
              "perspective guidelines, and simple primary volumes (spheres, ovals, cylinders, boxes). No contours, no shading."),
    StageSpec(2, "Primary Contour & Block-in", "Structural silhouette",
              "Draw the outer silhouette and key anchor points over the scaffolding. The guides stay visible underneath.",
              "keep ALL panel-1 lines exactly, and add medium graphite lines for the outer silhouette and the main "
              "anatomical / structural anchor points. Still no shading."),
    StageSpec(3, "Secondary Features & Plane Breaks", "Internal structure",
              "Add features, structural seams, secondary forms, and the core-shadow (terminator) boundaries.",
              "keep ALL previous lines exactly, and add secondary features (eyes, nose, seams, folds), plane breaks, "
              "and thin core-shadow terminator lines. Still no tone fill."),
    StageSpec(4, "Value, Hatching & Depth", "Planar shading",
              "Build value with directional hatching and cross-hatching in the shadow planes, plus ambient occlusion.",
              "keep ALL previous lines exactly, and add directional hatching and cross-hatching inside shadow planes, "
              "darker where forms turn away from the light, plus occlusion shadow."),
    StageSpec(5, "Line Weight & Fine Details", "Accents & finish",
              "Final selective dark accents where forms overlap, texture marks, and preserved highlights.",
              "keep ALL previous marks exactly, and add only selective heavy dark accents at overlaps and contact "
              "shadows, small texture marks, and a few crisp details. This is the finished drawing."),
]

PAINT_STAGES: list[StageSpec] = [
    StageSpec(1, "Imprimatura & Underdrawing", "Toned ground",
              "Kill the white canvas with a warm transparent wash, then place proportions with loose brush lines.",
              "the whole canvas covered in a flat warm transparent burnt-sienna wash, with loose dark-umber brush "
              "lines placing the main proportions. Nothing else."),
    StageSpec(2, "Tonal Block-in (Grisaille)", "Value massing",
              "Big brush passes that separate dark masses, mid-tones and lights. No details allowed.",
              "the same composition, now blocked in with 3-4 flat value masses (darks, mid-tones, lights) in "
              "monochrome umber/grey using big brush strokes. Absolutely no detail or edges refinement."),
    StageSpec(3, "Local Colour & Temperature", "Colour mapping",
              "Lay dominant local colours over the values: warm shadows, cool lights.",
              "paint dominant flat local colours over the value masses, keeping the same shapes; shadows warm, "
              "lights cool. Still broad strokes, no small detail."),
    StageSpec(4, "Half-tones & Edge Control", "Form modelling",
              "Model the form with half-tones, decide hard vs soft edges, and push atmospheric depth.",
              "keep the same colour shapes and model the forms with half-tone transitions, soften turning edges, "
              "keep a few hard edges at focal points, and add atmospheric depth."),
    StageSpec(5, "Highlights & Glazes", "Finish",
              "Small detail strokes, impasto highlights, specular reflections and chromatic accents.",
              "keep everything and add only small detail strokes, thick impasto highlights, specular reflections "
              "and a few saturated chromatic accents. This is the finished painting."),
]

PIXEL_STAGES: list[StageSpec] = [
    StageSpec(1, "Silhouette Outline", "Outline",
              "A clean 1-pixel outline that fixes the sprite's proportions.",
              "only a clean 1-pixel dark outline of the sprite silhouette on a plain background."),
    StageSpec(2, "Flat Colour Fill", "Base palette",
              "Fill each region with a flat base colour from a small palette.",
              "the same outline, with each region filled with one flat base colour from a limited palette."),
    StageSpec(3, "Shadow Shading", "Shading",
              "Add one shadow tone per colour on the side away from the light.",
              "add one darker shade per colour on the side away from the light."),
    StageSpec(4, "Highlights", "Highlights",
              "Add highlight pixels on the lit side.",
              "add lighter highlight pixels on the lit side."),
    StageSpec(5, "Polish", "Selective outline & detail",
              "Colour the outline selectively and add final detail pixels.",
              "recolour parts of the outline selectively and add final detail pixels. Finished sprite."),
]

MODE_STAGES = {"sketch": SKETCH_STAGES, "paint": PAINT_STAGES, "pixel": PIXEL_STAGES}

MODE_STYLE = {
    "sketch": "graphite pencil drawing on plain white paper, academic atelier construction method",
    "paint": "traditional oil painting, atelier indirect painting method",
    "pixel": "pixel art sprite, crisp hard pixels, no anti-aliasing, limited palette, plain flat background",
}
