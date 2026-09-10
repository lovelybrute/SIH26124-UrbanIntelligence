from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone

import cv2
import httpx
from ultralytics import YOLO


async def run(source: str, weights: str, api_url: str, bus_id: str, camera_id: str, lat: float, lon: float, conf: float) -> None:
    model = YOLO(weights)
    capture = cv2.VideoCapture(0 if source == "0" else source)
    if not capture.isOpened():
        raise RuntimeError(f"Unable to open source: {source}")

    last_emit: dict[str, int] = {}
    frame_index = 0

    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            ok, frame = capture.read()
            if not ok:
                break
            frame_index += 1
            results = model.predict(frame, conf=conf, verbose=False)

            for result in results:
                names = result.names
                if result.boxes is None:
                    continue
                for box in result.boxes:
                    score = float(box.conf[0])
                    label = str(names[int(box.cls[0])]).lower().replace(" ", "_")
                    x1, y1, x2, y2 = [int(v) for v in box.xyxy[0].tolist()]
                    event_type = "pothole" if "pothole" in label else "road_damage"
                    severity = 5 if score >= .9 else 4 if score >= .8 else 3

                    if frame_index - last_emit.get(label, -9999) >= 45:
                        payload = {
                            "bus_id": bus_id,
                            "camera_id": camera_id,
                            "event_type": event_type,
                            "location": {"latitude": lat, "longitude": lon},
                            "confidence": score,
                            "severity": severity,
                            "observed_at": datetime.now(timezone.utc).isoformat(),
                            "metadata": {"class_name": label, "bbox": [x1, y1, x2, y2], "frame_index": frame_index},
                        }
                        try:
                            response = await client.post(f"{api_url.rstrip('/')}/api/v1/events", json=payload)
                            response.raise_for_status()
                            last_emit[label] = frame_index
                        except httpx.HTTPError:
                            pass

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 255, 255), 2)
                    cv2.putText(frame, f"{label} {score:.2f}", (x1, max(20, y1 - 8)), cv2.FONT_HERSHEY_SIMPLEX, .5, (255, 255, 255), 1)

            cv2.imshow("SIH26124 Road Damage Reporter", frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    capture.release()
    cv2.destroyAllWindows()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="0")
    parser.add_argument("--weights", required=True)
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--bus", default="HYD-BUS-001")
    parser.add_argument("--camera", default="front-01")
    parser.add_argument("--lat", type=float, default=17.385044)
    parser.add_argument("--lon", type=float, default=78.486671)
    parser.add_argument("--conf", type=float, default=.55)
    args = parser.parse_args()
    asyncio.run(run(args.source, args.weights, args.api, args.bus, args.camera, args.lat, args.lon, args.conf))


if __name__ == "__main__":
    main()
