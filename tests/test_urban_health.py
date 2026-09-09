from types import SimpleNamespace

from backend.app.urban_health import summarize_city


def event(event_type: str, severity: int, confidence: float):
    return SimpleNamespace(event_type=event_type, severity=severity, confidence=confidence)


def issue(event_type: str, confidence: float, sightings: int):
    return SimpleNamespace(
        event_type=event_type,
        latitude=17.385,
        longitude=78.486,
        confidence=confidence,
        sightings=sightings,
    )


def test_city_health_scores_and_priorities():
    result = summarize_city(
        [
            event("pothole", 4, 0.9),
            event("traffic_congestion", 5, 0.8),
            event("pedestrian_risk", 4, 0.95),
        ],
        [issue("pothole", 0.9, 4), issue("waterlogging", 0.8, 2)],
    )

    assert result["road_health_score"] < 100
    assert result["congestion_index"] > 0
    assert result["safety_risk_score"] > 0
    assert result["priority_issues"][0]["event_type"] == "pothole"
