"""
Shared layer model.

A tutorial is a stack of N layers. layer_k holds ONLY the marks added at stage k
(transparent everywhere else). The canvas at stage k is, by definition:

    composite_k = alpha_composite(composite_{k-1}, layer_k)      composite_0 = background

Because composites are *derived* from the layers (never taken straight from the model),
stage k can't lose anything that was on the canvas at stage k-1 except where layer_k
deliberately paints over it. That is the continuity guarantee; `verify_stack` checks it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from PIL import Image


@dataclass
class StageLayer:
    layer: Image.Image      # RGBA, only this stage's new marks
    composite: Image.Image  # RGBA, the whole canvas after this stage

    @property
    def coverage(self) -> float:
        """Fraction of the canvas touched by this stage."""
        alpha = np.asarray(self.layer)[..., 3]
        return float((alpha > 0).mean())


@dataclass
class LayerStack:
    background: Image.Image
    stages: list[StageLayer] = field(default_factory=list)

    def push(self, layer: Image.Image) -> StageLayer:
        prev = self.stages[-1].composite if self.stages else self.background
        stage = StageLayer(layer=layer, composite=Image.alpha_composite(prev, layer))
        self.stages.append(stage)
        return stage


@dataclass
class ContinuityReport:
    verified: bool
    max_untouched_drift: int  # max channel difference in pixels the stage did NOT paint (must be 0)
    details: list[str]


def verify_stack(stack: LayerStack) -> ContinuityReport:
    """Re-check the invariant independently of how the stack was built."""
    details: list[str] = []
    worst = 0
    prev = np.asarray(stack.background).astype(np.int16)
    for i, st in enumerate(stack.stages, start=1):
        cur = np.asarray(st.composite).astype(np.int16)
        untouched = np.asarray(st.layer)[..., 3] == 0
        drift = int(np.abs(cur - prev)[untouched].max()) if untouched.any() else 0
        worst = max(worst, drift)
        if drift:
            details.append(f"stage {i}: {drift} drift in unpainted pixels")
        prev = cur
    return ContinuityReport(verified=worst == 0, max_untouched_drift=worst, details=details)
