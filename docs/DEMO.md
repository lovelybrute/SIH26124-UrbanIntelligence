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

Six simulated buses will repeatedly observe realistic urban hotspots around Hyderabad coordinates. Nearby repeated observations are correlated into a single issue with growing confidence.

## 3. Start command center

```bash
cd frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

The dashboard should show:

- active bus count
- raw event count
- correlated urban issues
- persisted event count
- road-health score
- congestion index
- safety-risk score
- spatially plotted issue markers
- priority issues ranked by confidence and repeat sightings

## 4. Train road-damage model

Place a YOLO-format road-damage dataset under `datasets/road_damage`, update `data.yaml`, then run:

```bash
python edge_ai/road_damage/train.py
```

## 5. Run camera/video road-damage inference

```bash
python edge_ai/road_damage/infer_video.py --weights path/to/best.pt --source camera
```

or

```bash
python edge_ai/road_damage/infer_video.py --weights path/to/best.pt --source road_video.mp4
```

## What is real vs simulated

The API, persistence, correlation logic, analytics and command-center updates are functional software. The fleet script generates simulated edge detections for demonstration. Real road-damage accuracy depends on a properly trained and evaluated model; no accuracy claim should be made until the chosen dataset and trained weights are validated.
