"""Run trained road-damage detection on a camera or video source."""

import argparse
from pathlib import Path

import cv2
from ultralytics import YOLO


def run(weights: str, source: str, confidence: float = 0.35) -> None:
    model = YOLO(weights)
    cap = cv2.VideoCapture(0 if source == "camera" else source)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open source: {source}")

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break
            result = model.predict(frame, conf=confidence, verbose=False)[0]
            annotated = result.plot()
            cv2.imshow("SIH26124 Road Intelligence", annotated)
            if cv2.waitKey(1) & 0xFF in (27, ord("q")):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--weights", default="models/road_damage/best.pt")
    parser.add_argument("--source", default="camera", help="camera or path to a video")
    parser.add_argument("--confidence", type=float, default=0.35)
    args = parser.parse_args()
    run(args.weights, args.source, args.confidence)
