# Dataset and Model Evidence

## Road damage: RDD2022

Primary road-damage training source: **RDD2022 (The Multi-National Road Damage Dataset 2022)**.

Verified source facts:
- 47,420 road images from Japan, India, Czech Republic, Norway, United States and China.
- Four labeled road-damage types: longitudinal crack (D00), transverse crack (D10), alligator crack (D20) and pothole (D40).
- Training annotations are Pascal VOC XML bounding boxes.
- The Figshare release states **CC BY 4.0**.

Official resources:
- Project repository: `https://github.com/sekilab/RoadDamageDetector`
- Figshare record: `https://figshare.com/articles/dataset/21431547`

Always cite the dataset authors in reports/submissions and retain the source attribution.

## Prepare data

The repository intentionally does not commit multi-GB datasets.

To download the full official archive and prepare only India initially:

```bash
python scripts/prepare_rdd2022.py --download --country India
```

If RDD2022 is already extracted locally:

```bash
python scripts/prepare_rdd2022.py --source path/to/RDD2022 --country India
```

To prepare every country from an already extracted archive:

```bash
python scripts/prepare_rdd2022.py --source path/to/RDD2022 --country ""
```

The converter creates deterministic 80/10/10 train/validation/test splits under `datasets/road_damage/processed` and converts Pascal VOC boxes to YOLO format.

## Classes used by SentinelTrace Urban Intelligence

| RDD2022 code | YOLO class | Backend event |
| --- | --- | --- |
| D00 | longitudinal_crack | road_damage |
| D10 | transverse_crack | road_damage |
| D20 | alligator_crack | road_damage |
| D40 | pothole | pothole |

Waterlogging, missing signs, zebra crossings and divider defects are **not labeled by RDD2022**. They require separate labeled data/models and must not be represented as validated RDD2022 capabilities.

## Train and evaluate

```bash
python edge_ai/road_damage/train.py
python edge_ai/road_damage/evaluate.py --weights models/road_damage/sih26124-road-damage/weights/best.pt
```

Do not place accuracy numbers in the SIH presentation until `evaluate.py` has generated them from actual held-out data.
