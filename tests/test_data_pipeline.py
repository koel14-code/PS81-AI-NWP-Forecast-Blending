import pandas as pd

from src.data.ingestion import NWPDataLoader
from src.data.preprocessing import align_to_reference, normalize_columns
from src.features.feature_engineering import FeatureEngineer
from src.models.regression import BlendingRegressor


def test_loader_reads_csv_rows():
    data = pd.DataFrame(
        {
            "time": ["2024-01-01T00:00:00", "2024-01-01T06:00:00"],
            "lat": [12.0, 12.5],
            "lon": [75.0, 75.5],
            "GFS": [10.0, 20.0],
            "ECMWF": [12.0, 18.0],
            "target": [9.0, 19.0],
        }
    )
    loader = NWPDataLoader(model_names=["GFS", "ECMWF"])
    loaded = loader.read_csv(data)
    assert list(loaded.columns) == ["time", "lat", "lon", "GFS", "ECMWF", "target"]


def test_align_to_reference_reindexes_and_fills_missing():
    source = pd.DataFrame({"lat": [10.0, 12.0], "lon": [70.0, 72.0], "GFS": [1.0, 2.0]})
    reference = pd.DataFrame({"lat": [10.0, 11.0, 12.0], "lon": [70.0, 71.0, 72.0]})
    aligned = align_to_reference(source, reference, value_cols=["GFS"])
    assert aligned.shape[0] == 3
    assert "GFS" in aligned.columns


def test_feature_engineer_creates_model_inputs():
    df = pd.DataFrame({"GFS": [1.0, 2.0], "ECMWF": [3.0, 4.0], "target": [5.0, 6.0], "lead_time_hours": [24, 48]})
    engineer = FeatureEngineer()
    features = engineer.build_features(df)
    assert "GFS" in features.columns
    assert "ECMWF" in features.columns
    assert "lead_time_hours" in features.columns


def test_blending_regressor_predicts_constant_output():
    model = BlendingRegressor(weights={"GFS": 0.6, "ECMWF": 0.4})
    X = pd.DataFrame({"GFS": [1.0, 2.0], "ECMWF": [3.0, 4.0]})
    prediction = model.predict(X)
    assert len(prediction) == 2
    assert prediction[0] > 0
