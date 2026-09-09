from statistics import mean

ROAD_ISSUES = {"pothole", "road_damage", "waterlogging", "road_infrastructure"}
SAFETY_ISSUES = {"pedestrian_risk", "vehicle_incident"}


def summarize_city(events: list, issues: list) -> dict:
    road = [e for e in events if e.event_type in ROAD_ISSUES]
    congestion = [e for e in events if e.event_type == "traffic_congestion"]
    safety = [e for e in events if e.event_type in SAFETY_ISSUES]

    road_penalty = sum(e.severity * e.confidence for e in road) * 1.6
    road_health = max(0.0, min(100.0, 100.0 - road_penalty))
    congestion_index = mean([e.severity * e.confidence * 20 for e in congestion]) if congestion else 0.0
    safety_risk = mean([e.severity * e.confidence * 20 for e in safety]) if safety else 0.0

    ranked = sorted(
        issues,
        key=lambda issue: issue.confidence * max(issue.sightings, 1),
        reverse=True,
    )[:10]

    return {
        "road_health_score": round(road_health, 1),
        "congestion_index": round(max(0.0, min(100.0, congestion_index)), 1),
        "safety_risk_score": round(max(0.0, min(100.0, safety_risk)), 1),
        "priority_issues": [
            {
                "event_type": x.event_type,
                "latitude": x.latitude,
                "longitude": x.longitude,
                "confidence": round(x.confidence, 4),
                "sightings": x.sightings,
                "priority_score": round(x.confidence * max(x.sightings, 1), 3),
            }
            for x in ranked
        ],
    }
