from backend.app.ambulance import build_priority_alert
from backend.app.geojson import issues_to_feature_collection
from backend.app.workflow import AuthorityWorkflow


def test_authority_workflow_lifecycle():
    workflow = AuthorityWorkflow()
    item = workflow.create("pothole", 17.38, 78.48, severity=4, confidence=0.95)
    assert item.status == "detected"

    updated = workflow.update(item.id, "assigned", assignee="Road Maintenance", note="Crew notified")
    assert updated.status == "assigned"
    assert updated.assignee == "Road Maintenance"
    assert updated.notes == ["Crew notified"]


def test_ambulance_priority_alert_has_eta():
    alert = build_priority_alert("AMB-01", 17.38, 78.48, 17.40, 78.50, avg_speed_kmh=40)
    assert alert.distance_km > 0
    assert alert.eta_minutes > 0
    assert alert.priority in {"critical", "high", "standard"}


def test_empty_geojson_collection():
    data = issues_to_feature_collection([])
    assert data == {"type": "FeatureCollection", "features": []}
