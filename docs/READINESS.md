# SIH26124 Readiness Checklist

This document distinguishes implemented software from results that require real data or deployment verification.

## Implemented software

- FastAPI event ingestion and health/status endpoints
- Durable SQLite event storage
- Multi-bus event correlation and confidence fusion
- Urban health, congestion and safety analytics
- GeoJSON issue/event feeds
- MapLibre/OpenStreetMap command center
- Authority workflow with persistence and dashboard actions
- Ambulance priority/ETA extension
- YOLO vehicle/pedestrian edge inference
- Road-damage training and inference pipeline
- Road-damage evaluation script producing precision, recall, mAP@50 and mAP@50:95
- Vehicle tracking and motion-anomaly incident signals
- EasyOCR ANPR adapter and ANPR evaluation utility
- Evidence image upload and serving
- Docker Compose deployment configuration
- Backend tests and frontend production-build CI

## Demonstration / simulation components

- Multi-bus fleet generator
- Simulated pothole/waterlogging/congestion/pedestrian-risk observations
- Static GPS coordinates when a physical GPS feed is not connected
- Ambulance priority is an optional extension and is not claimed as a core SIH26124 requirement

## Requires real data before accuracy claims

### Road-damage AI

1. Place an annotated YOLO dataset under `datasets/road_damage`.
2. Train with `python edge_ai/road_damage/train.py`.
3. Evaluate the final weights with:

```bash
python edge_ai/road_damage/evaluate.py --weights models/road_damage/.../weights/best.pt --split test
```

The generated `reports/road_damage_metrics.json` is the only source that should be used for model precision/recall/mAP claims.

### ANPR

Create a directory containing plate images and a `labels.json` file such as:

```json
{
  "plate_001.jpg": "TS09AB1234",
  "plate_002.jpg": "KA01MN4321"
}
```

Then run:

```bash
python -m edge_ai.anpr_evaluate path/to/anpr_eval
```

Use `reports/anpr_metrics.json` for ANPR accuracy claims.

## Final judge demo sequence

1. Start API and command center with Docker Compose or local commands.
2. Run the fleet simulator to demonstrate multi-bus correlation and GIS analytics.
3. Show authority work items being created and moved through the lifecycle.
4. Run a real camera/video through the edge vision runner.
5. If trained road-damage weights are available, run real pothole inference and show resulting events on GIS.
6. Show OCR/evidence events only with images where OCR actually succeeds.
7. Present evaluation JSON files and avoid unsupported accuracy claims.

## Definition of project-complete

The software platform can be considered feature-complete when all application modules above run end-to-end. The AI validation portion is complete only after labeled road-damage and ANPR datasets have been evaluated and their generated reports have been reviewed.
