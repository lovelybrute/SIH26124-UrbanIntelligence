# SIH26124 Demo Runbook

## 1. Start backend

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to inspect the API.

## 2. Start multi-bus simulation

```bash
python edge_ai/simulate_fleet.py
```

Six simulated buses repeatedly observe urban hotspots around Hyderabad coordinates. Nearby repeated observations are correlated into a single issue with growing confidence and severe issues automatically create authority work items.

## 3. Start command center

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`. The dashboard includes the live OpenStreetMap GIS layer, city-health metrics, fleet nodes, priority intelligence and authority Start/Resolve controls.

## 4. Run the real vehicle/pedestrian edge camera

```bash
pip install -r requirements-vision.txt
python -m edge_ai.live_camera --source 0
```

Use a video path instead of `0` for recorded footage. Add `--ocr` to enable EasyOCR plate extraction:

```bash
python -m edge_ai.live_camera --source road_video.mp4 --ocr
```

The edge process performs YOLO detection, centroid tracking, scene-relative motion anomaly detection, optional OCR and evidence snapshot upload. Incident motion values are explicitly scene-relative pixels/second; they are not claimed as km/h without camera calibration.

## 5. Train road-damage model

Place a YOLO-format road-damage dataset under `datasets/road_damage`, update `data.yaml`, then run:

```bash
python edge_ai/road_damage/train.py
```

## 6. Run road-damage inference

```bash
python edge_ai/road_damage/infer_video.py --weights path/to/best.pt --source camera
```

or use a road video path as the source. The reporting runner can also post pothole/road-damage detections to the central API.

## 7. Docker demo

```bash
docker compose up --build
```

Backend: `http://localhost:8000`  
Command center: `http://localhost:5173`

## Evidence and authority workflow

Selected forensic JPEG evidence is uploaded to `/api/v1/evidence` and served from `/evidence/<file>`. High-severity road/safety events create authority work items that can transition through operational states from the dashboard.

## What is real vs simulated

The API, SQLite persistence, correlation logic, analytics, GIS, authority workflow, evidence storage, edge YOLO pipeline, tracking, OCR adapter and command-center controls are functional software. The fleet script is deliberately simulated for repeatable demonstration. Road-damage and ANPR accuracy must be reported only after training/evaluating on a documented dataset; the repository does not invent accuracy numbers.
