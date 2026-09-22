from __future__ import annotations

from typing import Sequence

import pandas as pd


def normalize_columns(df: pd.DataFrame, rename_map: dict | None = None) -> pd.DataFrame:
    """Standardize coordinate fields while preserving model names such as GFS."""
    df = df.copy()
    if rename_map:
        df = df.rename(columns=rename_map)

    normalized = {}
    for col in df.columns:
        key = str(col).strip()
        if key.lower() in {"lat", "lon", "time"}:
            normalized[col] = key.lower()
        else:
            normalized[col] = key
    return df.rename(columns=normalized)


def align_to_reference(source: pd.DataFrame, reference: pd.DataFrame, value_cols: Sequence[str] | None = None) -> pd.DataFrame:
    """Align source rows to a reference grid and fill missing values with 0.0."""
    source = normalize_columns(source)
    reference = normalize_columns(reference)

    value_cols = list(value_cols or source.columns)
    resolved_cols = []
    for col in value_cols:
        match = next((c for c in source.columns if c.lower() == str(col).lower()), None)
        if match is not None and match not in {"lat", "lon", "time"}:
            resolved_cols.append(match)

    reference_grid = reference[["lat", "lon"]].drop_duplicates().reset_index(drop=True)
    source_values = source[["lat", "lon", *resolved_cols]].drop_duplicates().reset_index(drop=True)

    merged = reference_grid.merge(source_values, on=["lat", "lon"], how="left")
    for col in resolved_cols:
        merged[col] = merged[col].fillna(0.0)

    return merged
