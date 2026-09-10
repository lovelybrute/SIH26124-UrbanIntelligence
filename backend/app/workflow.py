from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Literal
from uuid import uuid4

from .workflow_storage import load_work_items, save_work_item

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

    @classmethod
    def from_dict(cls, payload: dict) -> "WorkItem":
        return cls(**payload)


class AuthorityWorkflow:
    def __init__(self) -> None:
        self.items: dict[str, WorkItem] = {}
        for payload in load_work_items():
            try:
                item = WorkItem.from_dict(payload)
                self.items[item.id] = item
            except (TypeError, ValueError):
                continue

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
        save_work_item(item)
        return item

    def update(self, item_id: str, status: WorkflowStatus, assignee: str | None = None, note: str | None = None) -> WorkItem:
        item = self.items[item_id]
        item.status = status
        if assignee is not None:
            item.assignee = assignee
        if note:
            item.notes.append(note)
        item.updated_at = datetime.now(timezone.utc).isoformat()
        save_work_item(item)
        return item

    def list(self) -> list[dict]:
        return [item.to_dict() for item in sorted(self.items.values(), key=lambda x: x.updated_at, reverse=True)]
