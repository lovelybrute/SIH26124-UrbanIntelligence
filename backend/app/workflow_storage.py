from __future__ import annotations

import json
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(os.getenv("URBAN_DB_PATH", "urban_intelligence.db"))


def init_workflow_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS authority_work_items (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                payload_json TEXT NOT NULL
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_work_status ON authority_work_items(status)")


def save_work_item(item) -> None:
    init_workflow_db()
    payload = item.to_dict()
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO authority_work_items (id, status, updated_at, payload_json)
            VALUES (?, ?, ?, ?)
            """,
            (item.id, item.status, item.updated_at, json.dumps(payload)),
        )


def load_work_items() -> list[dict]:
    init_workflow_db()
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT payload_json FROM authority_work_items ORDER BY updated_at DESC"
        ).fetchall()
    return [json.loads(row[0]) for row in rows]
