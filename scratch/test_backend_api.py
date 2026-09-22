"""
Test runner for FastAPI backend endpoints.
"""

from fastapi.testclient import TestClient
from src.api.main import app

client = TestClient(app)

def test_endpoints():
    print("Testing FastAPI Backend Endpoints...")
    
    endpoints = [
        "/api/health",
        "/api/overview",
        "/api/forecast?location=kolkata&lead_day=1",
        "/api/forecast?location=delhi&lead_day=2",
        "/api/weights?location=mumbai&lead_day=1",
        "/api/spatial-weights?lead_day=1",
        "/api/verification",
        "/api/extreme-signal?location=guwahati&lead_day=1",
        "/api/methodology",
    ]

    for ep in endpoints:
        res = client.get(ep)
        assert res.status_code == 200, f"Endpoint {ep} failed with status {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("success") is True, f"Endpoint {ep} returned success=False"
        print(f"[PASS]: {ep}")

    print("ALL BACKEND ENDPOINTS VERIFIED SUCCESSFULLY!")

if __name__ == "__main__":
    test_endpoints()
