from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from math import hypot
from time import monotonic


@dataclass
class MotionSample:
    t: float
    cx: float
    cy: float


@dataclass
class IncidentSignal:
    track_id: str
    label: str
    pixel_speed: float
    acceleration: float
    risk: str


class IncidentEngine:
    """Lightweight motion anomaly engine for rash-driving demo signals.

    Pixel speed is intentionally treated as a scene-relative signal. Real km/h
    estimation requires camera calibration / homography and must not be inferred
    from pixels alone.
    """

    def __init__(self, history: int = 6, speed_threshold: float = 220.0, acceleration_threshold: float = 420.0):
        self.history = history
        self.speed_threshold = speed_threshold
        self.acceleration_threshold = acceleration_threshold
        self.samples: dict[str, deque[MotionSample]] = defaultdict(lambda: deque(maxlen=history))
        self.last_speed: dict[str, float] = {}

    def observe(self, track: dict, timestamp: float | None = None) -> IncidentSignal | None:
        track_id = str(track["track_id"])
        x1, y1, x2, y2 = track["bbox"]
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
        now = monotonic() if timestamp is None else timestamp
        history = self.samples[track_id]
        history.append(MotionSample(now, cx, cy))
        if len(history) < 2:
            return None

        a, b = history[-2], history[-1]
        dt = max(b.t - a.t, 1e-3)
        speed = hypot(b.cx - a.cx, b.cy - a.cy) / dt
        previous = self.last_speed.get(track_id, speed)
        acceleration = abs(speed - previous) / dt
        self.last_speed[track_id] = speed

        if acceleration >= self.acceleration_threshold:
            risk = "critical"
        elif speed >= self.speed_threshold:
            risk = "high"
        else:
            return None

        return IncidentSignal(
            track_id=track_id,
            label=str(track.get("label", "vehicle")),
            pixel_speed=round(speed, 2),
            acceleration=round(acceleration, 2),
            risk=risk,
        )
