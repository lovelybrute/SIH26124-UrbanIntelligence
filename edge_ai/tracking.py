from dataclasses import dataclass
from math import hypot


@dataclass
class Track:
    track_id: int
    cx: float
    cy: float
    label: str
    missed: int = 0


class CentroidTracker:
    def __init__(self, max_distance: float = 80.0, max_missed: int = 10):
        self.max_distance = max_distance
        self.max_missed = max_missed
        self.next_id = 1
        self.tracks: dict[int, Track] = {}

    def update(self, detections: list[dict]) -> list[dict]:
        unmatched_tracks = set(self.tracks)
        output = []

        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            candidates = []
            for tid in unmatched_tracks:
                tr = self.tracks[tid]
                if tr.label != det["label"]:
                    continue
                candidates.append((hypot(cx - tr.cx, cy - tr.cy), tid))

            if candidates and min(candidates)[0] <= self.max_distance:
                _, tid = min(candidates)
                tr = self.tracks[tid]
                tr.cx, tr.cy, tr.missed = cx, cy, 0
                unmatched_tracks.discard(tid)
            else:
                tid = self.next_id
                self.next_id += 1
                self.tracks[tid] = Track(tid, cx, cy, det["label"])

            output.append({**det, "track_id": str(tid)})

        for tid in list(unmatched_tracks):
            self.tracks[tid].missed += 1
            if self.tracks[tid].missed > self.max_missed:
                del self.tracks[tid]

        return output
