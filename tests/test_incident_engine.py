from edge_ai.incident_engine import IncidentEngine


def test_motion_anomaly_detects_large_scene_relative_jump():
    engine = IncidentEngine(speed_threshold=100.0, acceleration_threshold=200.0)
    track = {"track_id": "7", "label": "car", "bbox": (0, 0, 20, 20)}
    assert engine.observe(track, timestamp=0.0) is None

    moved = {"track_id": "7", "label": "car", "bbox": (200, 0, 220, 20)}
    signal = engine.observe(moved, timestamp=0.5)

    assert signal is not None
    assert signal.track_id == "7"
    assert signal.risk in {"high", "critical"}
    assert signal.pixel_speed > 100


def test_motion_anomaly_ignores_slow_track():
    engine = IncidentEngine(speed_threshold=100.0, acceleration_threshold=200.0)
    a = {"track_id": "3", "label": "bus", "bbox": (0, 0, 20, 20)}
    b = {"track_id": "3", "label": "bus", "bbox": (2, 0, 22, 20)}
    assert engine.observe(a, timestamp=0.0) is None
    assert engine.observe(b, timestamp=1.0) is None
