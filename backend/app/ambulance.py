from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from math import atan2, cos, radians, sin, sqrt


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = radians(lat1), radians(lat2)
    dp, dl = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dp / 2) ** 2 + cos(p1) * cos(p2) * sin(dl / 2) ** 2
    return 2 * r * atan2(sqrt(a), sqrt(1 - a))


@dataclass
class AmbulancePriorityAlert:
    vehicle_id: str
    latitude: float
    longitude: float
    destination_latitude: float
    destination_longitude: float
    distance_km: float
    eta_minutes: float
    priority: str
    generated_at: str

    def to_dict(self) -> dict:
        return asdict(self)


def build_priority_alert(
    vehicle_id: str,
    latitude: float,
    longitude: float,
    destination_latitude: float,
    destination_longitude: float,
    avg_speed_kmh: float = 35.0,
) -> AmbulancePriorityAlert:
    distance = haversine_km(latitude, longitude, destination_latitude, destination_longitude)
    speed = max(avg_speed_kmh, 5.0)
    eta = (distance / speed) * 60.0
    priority = "critical" if eta <= 5 else "high" if eta <= 12 else "standard"
    return AmbulancePriorityAlert(
        vehicle_id=vehicle_id,
        latitude=latitude,
        longitude=longitude,
        destination_latitude=destination_latitude,
        destination_longitude=destination_longitude,
        distance_km=round(distance, 3),
        eta_minutes=round(eta, 1),
        priority=priority,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )
