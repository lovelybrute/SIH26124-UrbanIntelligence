# SIH26124 Urban Intelligence

AI-powered mobile urban intelligence platform using public transport fleets as moving sensing nodes.

## Core Scope
- Pothole and road-damage detection
- Road infrastructure and waterlogging detection
- Vehicle/pedestrian detection and traffic density
- Vehicle tracking and ANPR-ready incident intelligence
- GPS, timestamp, severity and confidence metadata
- Multi-bus event correlation and deduplication
- Bandwidth-efficient edge processing
- Central GIS command center

## Architecture
`Bus Cameras -> Edge AI -> Event API -> PostgreSQL/PostGIS -> Analytics -> React GIS Command Center`

## Phase 1
The first milestone establishes a working FastAPI event-ingestion service, shared event schema, edge-bus simulator and production-oriented repository structure.

## Quick Start
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn backend.app.main:app --reload
```

Swagger: `http://127.0.0.1:8000/docs`

Run the simulated bus in another terminal:
```bash
python edge_ai/simulate_bus.py
```

## Roadmap
1. Core API/event schema
2. YOLO vehicle/pedestrian detector
3. Pothole/road-damage model
4. Tracking + traffic analytics
5. ANPR
6. Multi-bus correlation
7. PostgreSQL/PostGIS
8. React GIS dashboard
9. Incident workflow
10. Edge/Jetson optimization
