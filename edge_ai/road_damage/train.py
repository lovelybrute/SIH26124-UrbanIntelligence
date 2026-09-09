"""Train a YOLO road-damage model.

Expected dataset classes can include pothole, crack, damaged_road and waterlogging.
Place a YOLO-format dataset under datasets/road_damage and edit data.yaml paths.
"""

from pathlib import Path

from ultralytics import YOLO

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "datasets" / "road_damage" / "data.yaml"
OUT = ROOT / "models" / "road_damage"


def train(model_name: str = "yolo11n.pt", epochs: int = 60, imgsz: int = 640):
    if not DATA.exists():
        raise FileNotFoundError(f"Dataset config missing: {DATA}")

    model = YOLO(model_name)
    return model.train(
        data=str(DATA),
        epochs=epochs,
        imgsz=imgsz,
        project=str(OUT),
        name="sih26124-road-damage",
        patience=12,
        cache=False,
        plots=True,
    )


if __name__ == "__main__":
    train()
