import json
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("URBAN_DB_PATH", "urban_intelligence.db"))


def init_db() -> None:
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS urban_events (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                bus_id TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                observed_at TEXT NOT NULL,
                received_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_event_type ON urban_events(event_type)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_observed_at ON urban_events(observed_at)")


def save_event(event) -> None:
    payload = event.model_dump(mode="json")
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO urban_events
            (id, event_type, bus_id, latitude, longitude, observed_at, received_at, payload_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(event.id),
                event.event_type,
                event.bus_id,
                event.location.latitude,
                event.location.longitude,
                event.observed_at.isoformat(),
                event.received_at.isoformat(),
                json.dumps(payload),
            ),
        )


def recent_events(limit: int = 100) -> list[dict]:
    init_db()
    safe_limit = min(max(limit, 1), 1000)
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT payload_json FROM urban_events ORDER BY received_at DESC LIMIT ?",
            (safe_limit,),
        ).fetchall()
    return [json.loads(row[0]) for row in rows]


def persisted_count() -> int:
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        return int(conn.execute("SELECT COUNT(*) FROM urban_events").fetchone()[0])
