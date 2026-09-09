"""Edge detector interfaces.

Phase 1 keeps model execution behind stable interfaces so YOLO/ONNX/TensorRT
implementations can be added without changing event transport code.
"""

from dataclasses import dataclass


@dataclass(slots=True)
class Detection:
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]
    track_id: str | None = None


class UrbanDetector:
    """Base interface for onboard visual detectors."""

    def detect(self, frame) -> list[Detection]:
        raise NotImplementedError


class VehiclePedestrianDetector(UrbanDetector):
    """Placeholder for the YOLO vehicle/pedestrian model."""

    def detect(self, frame) -> list[Detection]:
        return []


class RoadDamageDetector(UrbanDetector):
    """Placeholder for pothole and road-surface-damage inference."""

    def detect(self, frame) -> list[Detection]:
        return []
