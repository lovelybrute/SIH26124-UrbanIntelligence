from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str]) -> None:
    print("+", " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare RDD2022, train YOLO, then evaluate the best road-damage model.")
    parser.add_argument("--source", default="datasets/rdd2022/raw")
    parser.add_argument("--country", default="India")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--epochs", type=int, default=60)
    parser.add_argument("--imgsz", type=int, default=640)
    parser.add_argument("--model", default="yolo11n.pt")
    args = parser.parse_args()

    prep = [sys.executable, "scripts/prepare_rdd2022.py", "--source", args.source, "--country", args.country]
    if args.download:
        prep.append("--download")
    run(prep)

    # Train through the Ultralytics CLI so every hyperparameter is visible in terminal logs.
    run([
        sys.executable, "-m", "ultralytics", "yolo", "detect", "train",
        f"model={args.model}",
        "data=datasets/road_damage/data.yaml",
        f"epochs={args.epochs}",
        f"imgsz={args.imgsz}",
        "project=models/road_damage",
        "name=sih26124-road-damage",
        "patience=12",
        "plots=True",
    ])

    weights = ROOT / "models/road_damage/sih26124-road-damage/weights/best.pt"
    if not weights.exists():
        raise FileNotFoundError(f"Training finished but best weights were not found: {weights}")

    run([sys.executable, "edge_ai/road_damage/evaluate.py", "--weights", str(weights)])

    manifest = {
        "dataset": "RDD2022",
        "country_filter": args.country,
        "base_model": args.model,
        "epochs": args.epochs,
        "imgsz": args.imgsz,
        "best_weights": str(weights.relative_to(ROOT)),
        "status": "training_and_evaluation_completed",
    }
    output = ROOT / "reports/road_damage/training_manifest.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Pipeline complete. Manifest: {output}")


if __name__ == "__main__":
    main()
