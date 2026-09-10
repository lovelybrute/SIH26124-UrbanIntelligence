def issues_to_feature_collection(issues) -> dict:
    features = []
    for issue in issues:
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [issue.longitude, issue.latitude],
            },
            "properties": {
                "event_type": issue.event_type,
                "sightings": issue.sightings,
                "confidence": round(issue.confidence, 4),
                "first_seen": issue.first_seen.isoformat() if hasattr(issue.first_seen, "isoformat") else str(issue.first_seen),
                "last_seen": issue.last_seen.isoformat() if hasattr(issue.last_seen, "isoformat") else str(issue.last_seen),
            },
        })
    return {"type": "FeatureCollection", "features": features}


def events_to_feature_collection(events) -> dict:
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [event.location.longitude, event.location.latitude]},
                "properties": {
                    "id": str(event.id),
                    "bus_id": event.bus_id,
                    "camera_id": event.camera_id,
                    "event_type": event.event_type,
                    "confidence": event.confidence,
                    "severity": event.severity,
                    "observed_at": event.observed_at.isoformat(),
                },
            }
            for event in events
        ],
    }
