from datetime import datetime, timezone

from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_liveness_and_readiness():
    live = client.get("/health/live")
    ready = client.get("/health/ready")
    assert live.status_code == 200
    assert live.json()["status"] == "ok"
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"


def test_event_ingestion_and_geojson():
    payload = {
        "bus_id": "TEST-BUS-001",
        "camera_id": "front-test",
        "event_type": "pothole",
        "location": {"latitude": 17.385044, "longitude": 78.486671},
        "confidence": 0.95,
        "severity": 4,
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "metadata": {"test": True},
    }
    created = client.post("/api/v1/events", json=payload)
    assert created.status_code == 201
    assert created.json()["event_type"] == "pothole"

    geo = client.get("/api/v1/gis/events.geojson")
    assert geo.status_code == 200
    body = geo.json()
    assert body["type"] == "FeatureCollection"
    assert any(f["properties"].get("event_type") == "pothole" for f in body["features"])


def test_invalid_evidence_type_rejected():
    response = client.post(
        "/api/v1/evidence",
        files={"file": ("payload.exe", b"not allowed", "application/octet-stream")},
    )
    assert response.status_code == 415
