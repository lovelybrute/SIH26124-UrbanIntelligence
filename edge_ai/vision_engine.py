from pathlib import Path

from .tracking import CentroidTracker

VEHICLE_LABELS = {"car", "motorcycle", "bus", "truck", "bicycle"}
PEDESTRIAN_LABELS = {"person"}


class VisionEngine:
    def __init__(self, model_path: str = "yolov8n.pt", confidence: float = 0.35):
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("Install ultralytics to use VisionEngine") from exc

        self.model = YOLO(model_path)
        self.confidence = confidence
        self.tracker = CentroidTracker()

    def infer(self, frame) -> list[dict]:
        results = self.model.predict(frame, conf=self.confidence, verbose=False)
        detections: list[dict] = []
        if not results:
            return detections

        result = results[0]
        names = result.names
        for box in result.boxes:
            cls_id = int(box.cls[0].item())
            label = names[cls_id]
            if label not in VEHICLE_LABELS | PEDESTRIAN_LABELS:
                continue
            x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
            detections.append({
                "label": label,
                "confidence": float(box.conf[0].item()),
                "bbox": (x1, y1, x2, y2),
            })

        return self.tracker.update(detections)
