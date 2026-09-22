from __future__ import annotations

import numpy as np
import pandas as pd


class BlendingRegressor:
    """A minimal placeholder regressor for rainfall blending predictions."""

    def __init__(self, bias: float = 0.0, weights: dict | None = None):
        self.bias = bias
        self.weights = weights or {}

    def fit(self, X, y):
        return self

    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            if self.weights:
                values = []
                for col, weight in self.weights.items():
                    if col in X.columns:
                        values.append(weight * X[col].to_numpy(dtype=float))
                if values:
                    return np.sum(np.vstack(values), axis=0) + self.bias
            return X.sum(axis=1).to_numpy(dtype=float) + self.bias

        X = np.asarray(X, dtype=float)
        if X.ndim == 1:
            X = X.reshape(1, -1)
        return np.sum(X, axis=1) + self.bias
