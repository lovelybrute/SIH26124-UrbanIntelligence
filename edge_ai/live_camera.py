from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone

import cv2
import httpx

from .vision_engine import YoloVisionEngine

VEHICLE_LABELS = {"car", "motorcycle", "bus", "truck", "bicycle"}


async def run(source: str, api_url: str, bus_id: str, camera_id: str, latitude: float, longitude: float, model: str) -> None:
    engine = YoloVisionEngine(model_path=model)
    capture = cv2.VideoCapture(0 if source == "0" else source)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open source: {source}")

    async with httpx.AsyncClient(timeout=10) as client:
        frame_index = 0
        while True:
            ok, frame = capture.read()
            if not ok:
                break

            frame_index += 1
            detections = engine.detect(frame)
            vehicle_count = sum(1 for d in detections if d.label in VEHICLE_LABELS)
            people = [d for d in detections if d.label == "person"]

            if frame_index % 15 == 0 and vehicle_count:
                payload = {
                    "bus_id": bus_id,
                    "camera_id": camera_id,
                    "event_type": "traffic_congestion",
                    "location": {"latitude": latitude, "longitude": longitude},
                    "confidence": min(0.99, 0.55 + vehicle_count * 0.03),
                    "severity": min(5, max(1, vehicle_count // 5 + 1)),
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                    "metadata": {"vehicle_count": vehicle_count, "frame_index": frame_index},
                }
                try:
                    await client.post(f"{api_url.rstrip('/')}/api/v1/events", json=payload)
                except httpx.HTTPError:
                    pass

            if frame_index % 20 == 0 and people:
                payload = {
                    "bus_id": bus_id,
                    "camera_id": camera_id,
                    "event_type": "pedestrian_risk",
                    "location": {"latitude": latitude, "longitude": longitude},
                    "confidence": max(d.confidence for d in people),
                    "severity": min(5, 1 + len(people) // 2),
                    "observed_at": datetime.now(timezone.utc).isoformat(),
                    "metadata": {"pedestrian_count": len(people), "frame_index": frame_index},
                }
                try:
                    await client.post(f"{api_url.rstrip('/')}/api/v1/events", json=payload)
                except httpx.HTTPError:
                    pass

            for detection in detections:
                x1, y1, x2, y2 = detection.bbox
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 1)
                cv2.putText(frame, f"{detection.label} {detection.confidence:.2f}", (x1, max(20, y1 - 5)), cv2.FONT_HERSHEY_SIMPLEX, .45, (255, 255, 255), 1)

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
    args = parser.parse_args()
    asyncio.run(run(args.source, args.api, args.bus, args.camera, args.lat, args.lon, args.model))


if __name__ == "__main__":
    main()
