import numpy as np

from src.blending.ensemble import WeightedEnsembleBlender
from src.data.ingestion import NWPDataLoader
from src.evaluation.metrics import rainfall_metrics
from src.features.feature_engineering import FeatureEngineer
from src.models.regression import BlendingRegressor
from src.utils.logging import setup_logger


def test_weighted_ensemble_blender_initializes():
    blender = WeightedEnsembleBlender(weights={"GFS": 0.5, "ECMWF": 0.5})
    assert blender.weights == {"GFS": 0.5, "ECMWF": 0.5}


def test_data_loader_exposes_source_names():
    loader = NWPDataLoader(model_names=["GFS", "NCUM"])
    assert loader.model_names == ["GFS", "NCUM"]


def test_feature_engineer_builds_features():
    engineer = FeatureEngineer()
    features = engineer.build_features(np.array([1.0, 2.0, 3.0]))
    assert features.shape == (3, 2)


def test_regressor_predicts_vector():
    model = BlendingRegressor()
    prediction = model.predict(np.array([[1.0, 2.0], [3.0, 4.0]]))
    assert prediction.shape == (2,)


def test_metrics_compute_expected_values():
    metrics = rainfall_metrics(np.array([1.0, 2.0]), np.array([1.0, 2.0]))
    assert metrics["rmse"] == 0.0
    assert metrics["mae"] == 0.0


def test_logger_is_created():
    logger = setup_logger("test_logger")
    assert logger.name == "test_logger"
