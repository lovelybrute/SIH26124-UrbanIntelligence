from __future__ import annotations

import argparse
import json
from pathlib import Path

from .anpr import normalize_plate
from .anpr_ocr import EasyOCRPlateReader


def evaluate(dataset_dir: str, gpu: bool = False) -> dict:
    root = Path(dataset_dir)
    labels_file = root / "labels.json"
    if not labels_file.exists():
        raise FileNotFoundError("Expected labels.json mapping image filenames to plate strings")

    labels = json.loads(labels_file.read_text(encoding="utf-8"))
    reader = EasyOCRPlateReader(gpu=gpu)

    total = 0
    exact = 0
    valid_reads = 0
    details = []

    for filename, expected in labels.items():
        image_path = root / filename
        if not image_path.exists():
            continue
        total += 1
        predictions = reader.read(str(image_path))
        best = predictions[0] if predictions else None
        predicted = best.text if best else ""
        confidence = best.confidence if best else 0.0
        if best and best.valid_format:
            valid_reads += 1
        ok = normalize_plate(predicted) == normalize_plate(expected)
        if ok:
            exact += 1
        details.append({
            "image": filename,
            "expected": normalize_plate(expected),
            "predicted": normalize_plate(predicted),
            "confidence": round(float(confidence), 4),
            "exact_match": ok,
        })

    report = {
        "samples_evaluated": total,
        "exact_match_accuracy": round(exact / total, 4) if total else 0.0,
        "valid_format_rate": round(valid_reads / total, 4) if total else 0.0,
        "details": details,
        "note": "Accuracy applies only to this labeled evaluation set and OCR configuration.",
    }

    out = Path("reports")
    out.mkdir(exist_ok=True)
    path = out / "anpr_metrics.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_dir")
    parser.add_argument("--gpu", action="store_true")
    args = parser.parse_args()
    evaluate(args.dataset_dir, args.gpu)


if __name__ == "__main__":
    main()
