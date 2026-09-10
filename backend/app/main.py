from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .ambulance import build_priority_alert
from .correlation import EventCorrelator
from .geojson import events_to_feature_collection, issues_to_feature_collection
from .storage import init_db, persisted_count, recent_events, save_event
from .urban_health import summarize_city
from .workflow import AuthorityWorkflow, WorkflowStatus

app = FastAPI(
    title="SIH26124 Urban Intelligence API",
    description="Central event-ingestion and decision-support API for AI-enabled public transport sensing nodes.",
    version="0.4.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

EventType = Literal[
    "pothole", "road_damage", "waterlogging", "road_infrastructure",
    "traffic_congestion", "pedestrian_risk", "vehicle_incident", "number_plate",
    "ambulance_priority",
]


class GeoPoint(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)


class UrbanEventIn(BaseModel):
    bus_id: str
    camera_id: str
    event_type: EventType
    location: GeoPoint
    confidence: float = Field(ge=0, le=1)
    severity: int = Field(default=1, ge=1, le=5)
    observed_at: datetime
    track_id: str | None = None
    plate_number: str | None = None
    evidence_uri: str | None = None
    metadata: dict = Field(default_factory=dict)


class UrbanEvent(UrbanEventIn):
    id: UUID
    received_at: datetime


class WorkflowCreate(BaseModel):
    event_type: str
    latitude: float
    longitude: float
    severity: int = Field(ge=1, le=5)
    confidence: float = Field(ge=0, le=1)


class WorkflowUpdate(BaseModel):
    status: WorkflowStatus
    assignee: str | None = None
    note: str | None = None


class AmbulanceRequest(BaseModel):
    vehicle_id: str
    latitude: float
    longitude: float
    destination_latitude: float
    destination_longitude: float
    avg_speed_kmh: float = Field(default=35.0, gt=0)


EVENTS: list[UrbanEvent] = []
CORRELATOR = EventCorrelator(radius_m=25.0)
WORKFLOW = AuthorityWorkflow()
init_db()


@app.get("/")
def health() -> dict:
    return {
        "project": "SIH26124 Urban Intelligence",
        "status": "online",
        "service": "central-event-api",
        "version": app.version,
        "events_received_this_process": len(EVENTS),
        "persisted_events": persisted_count(),
        "correlated_issues": len(CORRELATOR.issues),
        "authority_work_items": len(WORKFLOW.items),
    }


@app.post("/api/v1/events", response_model=UrbanEvent, status_code=201)
def ingest_event(payload: UrbanEventIn) -> UrbanEvent:
    event = UrbanEvent(
        **payload.model_dump(),
        id=uuid4(),
        received_at=datetime.now(timezone.utc),
    )
    EVENTS.append(event)
    CORRELATOR.observe(event)
    save_event(event)
    return event


@app.get("/api/v1/events", response_model=list[UrbanEvent])
def list_events(limit: int = 100) -> list[UrbanEvent]:
    safe_limit = min(max(limit, 1), 1000)
    return EVENTS[-safe_limit:]


@app.get("/api/v1/history")
def persisted_history(limit: int = 100) -> list[dict]:
    return recent_events(limit)


@app.get("/api/v1/issues")
def list_correlated_issues() -> list[dict]:
    return [
        {
            "event_type": issue.event_type,
            "latitude": issue.latitude,
            "longitude": issue.longitude,
            "first_seen": issue.first_seen,
            "last_seen": issue.last_seen,
            "sightings": issue.sightings,
            "confidence": round(issue.confidence, 4),
            "source_events": issue.source_events,
        }
        for issue in CORRELATOR.issues
    ]


@app.get("/api/v1/gis/issues.geojson")
def issues_geojson() -> dict:
    return issues_to_feature_collection(CORRELATOR.issues)


@app.get("/api/v1/gis/events.geojson")
def events_geojson(limit: int = 500) -> dict:
    safe_limit = min(max(limit, 1), 5000)
    return events_to_feature_collection(EVENTS[-safe_limit:])


@app.get("/api/v1/analytics/urban-health")
def urban_health() -> dict:
    return summarize_city(EVENTS, CORRELATOR.issues)


@app.post("/api/v1/authority/work-items", status_code=201)
def create_work_item(payload: WorkflowCreate) -> dict:
    return WORKFLOW.create(**payload.model_dump()).to_dict()


@app.get("/api/v1/authority/work-items")
def list_work_items() -> list[dict]:
    return WORKFLOW.list()


@app.patch("/api/v1/authority/work-items/{item_id}")
def update_work_item(item_id: str, payload: WorkflowUpdate) -> dict:
    try:
        return WORKFLOW.update(item_id, **payload.model_dump()).to_dict()
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Work item not found") from exc


@app.post("/api/v1/ambulance/priority")
def ambulance_priority(payload: AmbulanceRequest) -> dict:
    return build_priority_alert(**payload.model_dump()).to_dict()


@app.get("/api/v1/stats")
def stats() -> dict:
    counts: dict[str, int] = {}
    buses = set()
    for event in EVENTS:
        counts[event.event_type] = counts.get(event.event_type, 0) + 1
        buses.add(event.bus_id)
    return {
        "total_events": len(EVENTS),
        "persisted_events": persisted_count(),
        "correlated_issues": len(CORRELATOR.issues),
        "authority_work_items": len(WORKFLOW.items),
        "active_bus_ids": sorted(buses),
        "by_type": counts,
    }
