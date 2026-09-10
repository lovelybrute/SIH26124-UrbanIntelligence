from __future__ import annotations

import argparse
import hashlib
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

OFFICIAL_ARCHIVE = "https://bigdatacup.s3.ap-northeast-1.amazonaws.com/2022/CRDDC2022/RDD2022/RDD2022.zip"
CLASS_MAP = {"D00": 0, "D10": 1, "D20": 2, "D40": 3}
CLASS_NAMES = ["longitudinal_crack", "transverse_crack", "alligator_crack", "pothole"]


def split_for(key: str) -> str:
    value = int(hashlib.sha1(key.encode("utf-8")).hexdigest()[:8], 16) % 100
    if value < 80:
        return "train"
    if value < 90:
        return "val"
    return "test"


def find_image(xml_path: Path, root: Path) -> Path | None:
    tree = ET.parse(xml_path)
    filename = tree.getroot().findtext("filename")
    candidates = []
    if filename:
        candidates.extend(root.rglob(filename))
    if not candidates:
        for ext in (".jpg", ".jpeg", ".png", ".JPG"):
            candidates.extend(root.rglob(xml_path.stem + ext))
    return next(iter(candidates), None)


def convert_annotation(xml_path: Path) -> list[str]:
    root = ET.parse(xml_path).getroot()
    width = float(root.findtext("size/width") or 0)
    height = float(root.findtext("size/height") or 0)
    if width <= 0 or height <= 0:
        return []

    labels: list[str] = []
    for obj in root.findall("object"):
        name = (obj.findtext("name") or "").strip()
        if name not in CLASS_MAP:
            continue
        box = obj.find("bndbox")
        if box is None:
            continue
        xmin = float(box.findtext("xmin") or 0)
        ymin = float(box.findtext("ymin") or 0)
        xmax = float(box.findtext("xmax") or 0)
        ymax = float(box.findtext("ymax") or 0)
        x = ((xmin + xmax) / 2) / width
        y = ((ymin + ymax) / 2) / height
        w = max(0.0, xmax - xmin) / width
        h = max(0.0, ymax - ymin) / height
        if w <= 0 or h <= 0:
            continue
        labels.append(f"{CLASS_MAP[name]} {x:.6f} {y:.6f} {w:.6f} {h:.6f}")
    return labels


def prepare(source: Path, output: Path, country: str | None) -> dict:
    xmls = list(source.rglob("*.xml"))
    if country:
        token = country.lower()
        xmls = [p for p in xmls if token in str(p).lower()]
    if not xmls:
        raise RuntimeError("No RDD2022 XML annotations found. Check --source/--country.")

    counts = {"train": 0, "val": 0, "test": 0, "objects": 0, "skipped": 0}
    for xml_path in sorted(xmls):
        image = find_image(xml_path, source)
        labels = convert_annotation(xml_path)
        if image is None or not labels:
            counts["skipped"] += 1
            continue
        relative_key = str(xml_path.relative_to(source))
        split = split_for(relative_key)
        image_dir = output / "images" / split
        label_dir = output / "labels" / split
        image_dir.mkdir(parents=True, exist_ok=True)
        label_dir.mkdir(parents=True, exist_ok=True)
        stem = hashlib.sha1(relative_key.encode()).hexdigest()[:10] + "_" + image.stem
        target_image = image_dir / f"{stem}{image.suffix.lower()}"
        shutil.copy2(image, target_image)
        (label_dir / f"{stem}.txt").write_text("\n".join(labels) + "\n", encoding="utf-8")
        counts[split] += 1
        counts["objects"] += len(labels)
    return counts


def download_archive(target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    print("Downloading the full official RDD2022 archive. This is a large download.")
    urllib.request.urlretrieve(OFFICIAL_ARCHIVE, target)


def main() -> None:
    parser = argparse.ArgumentParser(description="Convert RDD2022 Pascal VOC annotations to deterministic YOLO splits.")
    parser.add_argument("--source", type=Path, default=Path("datasets/rdd2022/raw"), help="Extracted RDD2022 root")
    parser.add_argument("--output", type=Path, default=Path("datasets/road_damage/processed"))
    parser.add_argument("--country", default="India", help="Country/path filter. Use '' for all countries.")
    parser.add_argument("--download", action="store_true", help="Download and extract the full official RDD2022 archive first")
    parser.add_argument("--archive", type=Path, default=Path("datasets/rdd2022/RDD2022.zip"))
    args = parser.parse_args()

    if args.download:
        if not args.archive.exists():
            download_archive(args.archive)
        args.source.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(args.archive) as archive:
            archive.extractall(args.source)

    counts = prepare(args.source, args.output, args.country or None)
    print("RDD2022 preparation complete:", counts)
    print("Classes:", CLASS_NAMES)


if __name__ == "__main__":
    main()
