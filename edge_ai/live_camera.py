from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone

import cv2
import httpx

from .incident_engine import IncidentEngine
from .tracking import CentroidTracker
from .vision_engine import YoloVisionEngine

VEHICLE_LABELS = {"car", "motorcycle", "bus", "truck"}


async def upload_jpeg(client: httpx.AsyncClient, api_url: str, image, name: str) -> str | None:
    ok, encoded = cv2.imencode(".jpg", image, [int(cv2.IMWRITE_JPEG_QUALITY), 86])
    if not ok:
        return None
    try:
        response = await client.post(
            f"{api_url.rstrip('/')}/api/v1/evidence",
            files={"file": (name, encoded.tobytes(), "image/jpeg")},
        )
        if response.is_success:
            return response.json().get("uri")
    except httpx.HTTPError:
        return None
    return None


async def post_event(client, api_url, *, bus_id, camera_id, event_type, latitude, longitude, confidence, severity, track_id=None, plate_number=None, evidence_uri=None, metadata=None):
    payload = {
        "bus_id": bus_id,
        "camera_id": camera_id,
        "event_type": event_type,
        "location": {"latitude": latitude, "longitude": longitude},
        "confidence": float(max(0.0, min(1.0, confidence))),
        "severity": int(max(1, min(5, severity))),
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "track_id": track_id,
        "plate_number": plate_number,
        "evidence_uri": evidence_uri,
        "metadata": metadata or {},
    }
    try:
        await client.post(f"{api_url.rstrip('/')}/api/v1/events", json=payload)
    except httpx.HTTPError:
        pass


async def run(source: str, api_url: str, bus_id: str, camera_id: str, latitude: float, longitude: float, model: str, enable_ocr: bool) -> None:
    engine = YoloVisionEngine(model_path=model)
    tracker = CentroidTracker()
    incidents = IncidentEngine()
    plate_reader = None
    if enable_ocr:
        from .anpr_ocr import EasyOCRPlateReader
        plate_reader = EasyOCRPlateReader(gpu=False)

    capture = cv2.VideoCapture(0 if source == "0" else source)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open source: {source}")

    last_plate_by_track: dict[str, str] = {}
    last_incident_frame: dict[str, int] = {}

    async with httpx.AsyncClient(timeout=15) as client:
        frame_index = 0
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            frame_index += 1

            detections = engine.detect(frame)
            raw = [{"label": d.label, "confidence": d.confidence, "bbox": d.bbox} for d in detections]
            tracked = tracker.update(raw)
            vehicles = [d for d in tracked if d["label"] in VEHICLE_LABELS]
            people = [d for d in tracked if d["label"] == "person"]

            if frame_index % 15 == 0 and vehicles:
                await post_event(client, api_url, bus_id=bus_id, camera_id=camera_id,
                    event_type="traffic_congestion", latitude=latitude, longitude=longitude,
                    confidence=min(0.99, 0.55 + len(vehicles) * 0.03), severity=min(5, max(1, len(vehicles) // 5 + 1)),
                    metadata={"vehicle_count": len(vehicles), "frame_index": frame_index})

            if frame_index % 20 == 0 and people:
                await post_event(client, api_url, bus_id=bus_id, camera_id=camera_id,
                    event_type="pedestrian_risk", latitude=latitude, longitude=longitude,
                    confidence=max(d["confidence"] for d in people), severity=min(5, 1 + len(people) // 2),
                    metadata={"pedestrian_count": len(people), "frame_index": frame_index})

            for vehicle in vehicles:
                x1, y1, x2, y2 = vehicle["bbox"]
                track_id = str(vehicle["track_id"])
                signal = incidents.observe(vehicle)
                if signal and frame_index - last_incident_frame.get(track_id, -9999) > 60:
                    crop = frame[max(0, y1):max(y1 + 1, y2), max(0, x1):max(x1 + 1, x2)]
                    evidence_uri = await upload_jpeg(client, api_url, crop if crop.size else frame, f"incident_{bus_id}_{track_id}.jpg")
                    await post_event(client, api_url, bus_id=bus_id, camera_id=camera_id,
                        event_type="vehicle_incident", latitude=latitude, longitude=longitude,
                        confidence=vehicle["confidence"], severity=5 if signal.risk == "critical" else 4,
                        track_id=track_id, evidence_uri=evidence_uri,
                        metadata={"motion_risk": signal.risk, "pixel_speed": signal.pixel_speed,
                                  "pixel_acceleration": signal.acceleration, "calibration_note": "scene-relative motion; not km/h"})
                    last_incident_frame[track_id] = frame_index

                if plate_reader and frame_index % 45 == 0:
                    crop = frame[max(0, y1):max(y1 + 1, y2), max(0, x1):max(x1 + 1, x2)]
                    if crop.size:
                        plates = [p for p in plate_reader.read(crop) if p.valid_format and p.confidence >= 0.35]
                        if plates:
                            best = plates[0]
                            if last_plate_by_track.get(track_id) != best.text:
                                evidence_uri = await upload_jpeg(client, api_url, crop, f"plate_{best.text}.jpg")
                                await post_event(client, api_url, bus_id=bus_id, camera_id=camera_id,
                                    event_type="number_plate", latitude=latitude, longitude=longitude,
                                    confidence=best.confidence, severity=2, track_id=track_id,
                                    plate_number=best.text, evidence_uri=evidence_uri,
                                    metadata={"ocr_engine": "easyocr", "vehicle_class": vehicle["label"]})
                                last_plate_by_track[track_id] = best.text

            for detection in tracked:
                x1, y1, x2, y2 = detection["bbox"]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)
                cv2.putText(frame, f"{detection['label']} #{detection['track_id']} {detection['confidence']:.2f}",
                            (x1, max(20, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, .45, (255, 255, 255), 1)

            cv2.imshow("SIH26124 Edge Vision", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    capture.release()
    cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="0", help="0 for webcam or video/RTSP path")
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--bus", default="HYD-BUS-001")
    parser.add_argument("--camera", default="front-01")
    parser.add_argument("--lat", type=float, default=17.385044)
    parser.add_argument("--lon", type=float, default=78.486671)
    parser.add_argument("--model", default="yolo11n.pt")
    parser.add_argument("--ocr", action="store_true", help="Enable optional EasyOCR plate extraction")
    args = parser.parse_args()
    asyncio.run(run(args.source, args.api, args.bus, args.camera, args.lat, args.lon, args.model, args.ocr))


if __name__ == "__main__":
    main()
