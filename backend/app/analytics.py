from collections import Counter
from math import radians, sin, cos, sqrt, atan2


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371000.0
    p1, p2 = radians(lat1), radians(lat2)
    dp = radians(lat2 - lat1)
    dl = radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


def traffic_density(vehicle_count: int, frame_area_px: int, avg_speed_kmh: float | None = None) -> dict:
    occupancy = 0.0 if frame_area_px <= 0 else min(vehicle_count / max(frame_area_px / 100000.0, 1.0), 100.0)
    speed_penalty = 0.0 if avg_speed_kmh is None else max(0.0, 40.0 - avg_speed_kmh) * 1.25
    score = min(100.0, occupancy * 8.0 + speed_penalty)
    level = "low" if score < 30 else "medium" if score < 60 else "high" if score < 80 else "critical"
    return {"score": round(score, 2), "level": level, "vehicle_count": vehicle_count}


def count_labels(labels: list[str]) -> dict[str, int]:
    return dict(Counter(labels))
