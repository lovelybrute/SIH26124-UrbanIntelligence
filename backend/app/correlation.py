from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from .analytics import haversine_m


@dataclass
class CorrelatedIssue:
    event_type: str
    latitude: float
    longitude: float
    first_seen: datetime
    last_seen: datetime
    sightings: int = 1
    confidence_sum: float = 0.0
    source_events: list[UUID] = field(default_factory=list)

    @property
    def confidence(self) -> float:
        if self.sightings <= 0:
            return 0.0
        base = self.confidence_sum / self.sightings
        corroboration = min(0.12, max(0, self.sightings - 1) * 0.03)
        return min(0.999, base + corroboration)


class EventCorrelator:
    def __init__(self, radius_m: float = 25.0):
        self.radius_m = radius_m
        self.issues: list[CorrelatedIssue] = []

    def observe(self, event) -> CorrelatedIssue:
        for issue in self.issues:
            if issue.event_type != event.event_type:
                continue
            distance = haversine_m(issue.latitude, issue.longitude, event.location.latitude, event.location.longitude)
            if distance <= self.radius_m:
                issue.sightings += 1
                issue.last_seen = event.observed_at
                issue.confidence_sum += event.confidence
                issue.source_events.append(event.id)
                return issue

        issue = CorrelatedIssue(
            event_type=event.event_type,
            latitude=event.location.latitude,
            longitude=event.location.longitude,
            first_seen=event.observed_at,
            last_seen=event.observed_at,
            confidence_sum=event.confidence,
            source_events=[event.id],
        )
        self.issues.append(issue)
        return issue
