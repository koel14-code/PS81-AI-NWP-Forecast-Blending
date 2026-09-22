from __future__ import annotations

import numpy as np
import pandas as pd


class FeatureEngineer:
    """Creates a minimal set of features for rainfall blending models."""

    def __init__(self, include_squared: bool = True):
        self.include_squared = include_squared

    def build_features(self, values):
        if isinstance(values, pd.DataFrame):
            features = values.copy()
            if self.include_squared:
                for col in features.select_dtypes(include=[np.number]).columns:
                    features[f"{col}_sq"] = features[col] ** 2
            return features

        arr = np.asarray(values, dtype=float)
        features = [arr]
        if self.include_squared:
            features.append(arr ** 2)
        return np.column_stack(features)
