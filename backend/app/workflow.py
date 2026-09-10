from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

WorkflowStatus = Literal["detected", "verified", "assigned", "in_progress", "resolved", "rejected"]


@dataclass
class WorkItem:
    id: str
    event_type: str
    latitude: float
    longitude: float
    severity: int
    confidence: float
    status: WorkflowStatus = "detected"
    assignee: str | None = None
    notes: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class AuthorityWorkflow:
    def __init__(self) -> None:
        self.items: dict[str, WorkItem] = {}

    def create(self, event_type: str, latitude: float, longitude: float, severity: int, confidence: float) -> WorkItem:
        item = WorkItem(
            id=str(uuid4()),
            event_type=event_type,
            latitude=latitude,
            longitude=longitude,
            severity=severity,
            confidence=confidence,
        )
        self.items[item.id] = item
        return item

    def update(self, item_id: str, status: WorkflowStatus, assignee: str | None = None, note: str | None = None) -> WorkItem:
        item = self.items[item_id]
        item.status = status
        if assignee is not None:
            item.assignee = assignee
        if note:
            item.notes.append(note)
        item.updated_at = datetime.now(timezone.utc).isoformat()
        return item

    def list(self) -> list[dict]:
        return [item.to_dict() for item in sorted(self.items.values(), key=lambda x: x.updated_at, reverse=True)]
