import math
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from src.api.main import app

client = TestClient(app)

CITIES = ["kolkata", "delhi", "mumbai", "chennai", "guwahati", "bengaluru"]
LEAD_DAYS = [1, 2, 3]
VARIABLES = ["precipitation", "temperature", "wind"]


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["status"] == "online"
    assert "precipitation" in data["supported_variables"]
    assert "temperature" in data["supported_variables"]
    assert "wind" in data["supported_variables"]
    assert data["variable_status"]["wind"] == "production_validated"


def test_api_overview_variables():
    for v in VARIABLES:
        res = client.get(f"/api/overview?variable={v}")
        assert res.status_code == 200
        data = res.json()["data"]
        assert data["variable"] == v
        assert data["unit"] in ["mm/h", "°C", "km/h"]
        if v in ["precipitation", "wind"]:
            assert data["status"] == "production_validated"
        else:
            assert data["status"] == "implemented_extension"


@pytest.mark.parametrize("city", CITIES)
@pytest.mark.parametrize("day", LEAD_DAYS)
def test_precipitation_forecast(city, day):
    res = client.get(f"/api/forecast?location={city}&lead_day={day}&variable=precipitation")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["variable"] == "precipitation"
    assert data["unit"] == "mm/h"
    assert len(data["series"]) == 24
    for pt in data["series"]:
        blend = pt["blended_precipitation"]
        assert not math.isnan(blend) and not math.isinf(blend)
        assert blend >= 0.0


@pytest.mark.parametrize("city", CITIES)
@pytest.mark.parametrize("day", LEAD_DAYS)
def test_temperature_forecast(city, day):
    res = client.get(f"/api/forecast?location={city}&lead_day={day}&variable=temperature")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["variable"] == "temperature"
    assert data["unit"] == "°C"
    assert len(data["series"]) == 24
    for pt in data["series"]:
        blend = pt["blended_temperature"]
        assert not math.isnan(blend) and not math.isinf(blend)
        assert 10.0 <= blend <= 55.0


@pytest.mark.parametrize("city", CITIES)
@pytest.mark.parametrize("day", LEAD_DAYS)
def test_wind_forecast(city, day):
    res = client.get(f"/api/forecast?location={city}&lead_day={day}&variable=wind")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["variable"] == "wind"
    assert data["unit"] == "km/h"
    assert len(data["series"]) == 24
    for pt in data["series"]:
        blend = pt["blended_wind"]
        assert not math.isnan(blend) and not math.isinf(blend)
        assert blend >= 0.0


def test_forecast_backward_compatibility():
    res = client.get("/api/forecast?location=kolkata&lead_day=1")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["variable"] == "precipitation"
    assert "blended_precipitation" in data["series"][0]


def test_weights_sum_to_one():
    for v in VARIABLES:
        for city in CITIES[:2]:
            res = client.get(f"/api/weights?location={city}&lead_day=1&variable={v}")
            assert res.status_code == 200
            data = res.json()["data"]
            means = data["means"]
            w_sum = means["ECMWF_IFS"] + means["NOAA_GFS"] + means["DWD_ICON"]
            assert abs(w_sum - 1.0) < 1e-3
            assert means["ECMWF_IFS"] >= 0.0
            assert means["NOAA_GFS"] >= 0.0
            assert means["DWD_ICON"] >= 0.0


def test_spatial_weights():
    for v in VARIABLES:
        res = client.get(f"/api/spatial-weights?lead_day=1&variable={v}")
        assert res.status_code == 200
        data = res.json()["data"]
        assert len(data["locations"]) == 6


def test_verification():
    res_p = client.get("/api/verification?variable=precipitation")
    assert res_p.status_code == 200
    assert len(res_p.json()["data"]["table"]) >= 4

    res_t = client.get("/api/verification?variable=temperature")
    assert res_t.status_code == 200
    table_t = res_t.json()["data"]["table"]
    skyblend_t = next(r for r in table_t if r["Approach"] == "SkyBlend_Temperature")
    assert abs(skyblend_t["MAE"] - 1.0144) < 1e-3

    res_w = client.get("/api/verification?variable=wind")
    assert res_w.status_code == 200
    table_w = res_w.json()["data"]["table"]
    skyblend_w = next(r for r in table_w if r["Approach"] == "SkyBlend_Wind")
    assert abs(skyblend_w["MAE"] - 2.3690) < 1e-3


def test_extreme_signal():
    res_p = client.get("/api/extreme-signal?location=kolkata&lead_day=1&variable=precipitation")
    assert res_p.status_code == 200
    assert res_p.json()["data"]["threshold"] == 1.0

    res_t = client.get("/api/extreme-signal?location=kolkata&lead_day=1&variable=temperature")
    assert res_t.status_code == 200
    assert res_t.json()["data"]["threshold"] == 38.0

    res_w = client.get("/api/extreme-signal?location=kolkata&lead_day=1&variable=wind")
    assert res_w.status_code == 200
    assert res_w.json()["data"]["threshold"] == 40.0
    assert "blended_wind" in res_w.json()["data"]["series"][0]


def test_methodology_stages():
    res = client.get("/api/methodology")
    assert res.status_code == 200
    data = res.json()["data"]
    assert len(data["pipeline_stages"]) == 10
    assert "production_vs_research" in data

    res_w = client.get("/api/methodology?variable=wind")
    assert res_w.status_code == 200
    data_w = res_w.json()["data"]
    assert "wind_methodology" in data_w
    assert len(data_w["wind_methodology"]["nwp_members"]) == 3
