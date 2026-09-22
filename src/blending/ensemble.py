from __future__ import annotations

from typing import Dict, Iterable, Mapping, Optional

import numpy as np


class WeightedEnsembleBlender:
    """Simple weighted blending model for multiple forecast sources."""

    def __init__(self, weights: Optional[Mapping[str, float]] = None):
        self.weights = dict(weights or {})

    def combine(self, predictions: Mapping[str, Iterable[float]] | Iterable[float]) -> np.ndarray:
        if isinstance(predictions, Mapping):
            if not self.weights:
                self.weights = {key: 1.0 / len(predictions) for key in predictions}
            combined = []
            for key, values in predictions.items():
                weight = self.weights.get(key, 1.0)
                arr = np.asarray(list(values), dtype=float)
                combined.append(weight * arr)
            if not combined:
                return np.asarray([], dtype=float)
            return np.sum(np.stack(combined, axis=0), axis=0) / sum(self.weights.get(k, 1.0) for k in predictions)
        arr = np.asarray(list(predictions), dtype=float)
        return arr
