from __future__ import annotations

import os
import re
from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

EVIDENCE_DIR = Path(os.getenv("EVIDENCE_DIR", "evidence"))
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)
_ALLOWED_EXT = {".jpg", ".jpeg", ".png", ".webp", ".mp4"}


def _safe_name(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name or "evidence")
    return cleaned[:80] or "evidence"


async def save_evidence(upload: UploadFile) -> dict:
    suffix = Path(upload.filename or "").suffix.lower()
    if suffix not in _ALLOWED_EXT:
        suffix = ".bin"
    filename = f"{uuid4().hex}_{_safe_name(Path(upload.filename or 'evidence').stem)}{suffix}"
    target = EVIDENCE_DIR / filename
    size = 0
    with target.open("wb") as handle:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            if size > 25 * 1024 * 1024:
                target.unlink(missing_ok=True)
                raise ValueError("Evidence file exceeds 25 MB")
            handle.write(chunk)
    return {"filename": filename, "size_bytes": size, "uri": f"/evidence/{filename}"}
