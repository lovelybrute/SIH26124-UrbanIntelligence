# System Architecture

## 1. Mobile Edge Layer
Each bus is treated as an independent sensing node. Front/rear/side cameras feed an edge pipeline containing object detection, road-damage detection, tracking, ANPR and event fusion.

Raw continuous video should remain local where possible. The node emits compact events containing type, confidence, GPS position, timestamp, severity and optional evidence references.

## 2. Ingestion Layer
FastAPI receives events from buses through versioned endpoints. Authentication, rate limiting and durable queues will be introduced before deployment.

## 3. Spatial Intelligence Layer
PostgreSQL + PostGIS will store bus telemetry and incidents. Nearby observations will be clustered so repeated detections of one pothole or infrastructure defect become a single evolving urban issue.

## 4. Analytics Layer
Planned services include congestion estimation, road-condition scoring, incident correlation, route-delay estimation, repeated-sighting confidence and repair verification.

## 5. Command Center
The React dashboard will expose a GIS map with live fleet locations, incident markers, traffic heatmaps, road-condition layers, evidence and authority workflows.

## Event Lifecycle

```text
Camera Frame
 -> Edge Detection
 -> Tracking / Classification
 -> Local Event Fusion
 -> GPS + Timestamp
 -> Event API
 -> Spatial Deduplication
 -> Database
 -> Analytics
 -> GIS Dashboard / Alert
```

## Privacy and Bandwidth
The design prioritizes edge processing. Full video does not need to be continuously uploaded; the platform can transmit event metadata and limited evidence only when policy permits and an actionable detection occurs.
