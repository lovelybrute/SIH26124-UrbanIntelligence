from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="SIH26124 Urban Intelligence API",
    description="Central event-ingestion API for AI-enabled public transport sensing nodes.",
    version="0.1.0",
)

EventType = Literal[
    "pothole",
    "road_damage",
    "waterlogging",
    "road_infrastructure",
    "traffic_congestion",
    "pedestrian_risk",
    "vehicle_incident",
    "number_plate",
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


EVENTS: list[UrbanEvent] = []


@app.get("/")
def health() -> dict:
    return {
        "project": "SIH26124 Urban Intelligence",
        "status": "online",
        "service": "central-event-api",
        "events_received": len(EVENTS),
    }


@app.post("/api/v1/events", response_model=UrbanEvent, status_code=201)
def ingest_event(payload: UrbanEventIn) -> UrbanEvent:
    event = UrbanEvent(
        **payload.model_dump(),
        id=uuid4(),
        received_at=datetime.now(timezone.utc),
    )
    EVENTS.append(event)
    return event


@app.get("/api/v1/events", response_model=list[UrbanEvent])
def list_events(limit: int = 100) -> list[UrbanEvent]:
    safe_limit = min(max(limit, 1), 1000)
    return EVENTS[-safe_limit:]


@app.get("/api/v1/stats")
def stats() -> dict:
    counts: dict[str, int] = {}
    for event in EVENTS:
        counts[event.event_type] = counts.get(event.event_type, 0) + 1
    return {"total_events": len(EVENTS), "by_type": counts}
