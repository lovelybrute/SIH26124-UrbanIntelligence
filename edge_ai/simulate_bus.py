"""Simulate a public-transport edge node sending compact AI events."""

import asyncio
import random
from datetime import datetime, timezone

import httpx

API_URL = "http://127.0.0.1:8000/api/v1/events"
BUS_ID = "HYD-BUS-001"
CAMERA_ID = "front-01"

EVENT_TYPES = [
    "pothole",
    "road_damage",
    "waterlogging",
    "traffic_congestion",
    "pedestrian_risk",
]


async def main() -> None:
    lat, lon = 17.385044, 78.486671

    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            lat += random.uniform(-0.0005, 0.0005)
            lon += random.uniform(-0.0005, 0.0005)
            event_type = random.choice(EVENT_TYPES)

            payload = {
                "bus_id": BUS_ID,
                "camera_id": CAMERA_ID,
                "event_type": event_type,
                "location": {"latitude": lat, "longitude": lon},
                "confidence": round(random.uniform(0.72, 0.99), 3),
                "severity": random.randint(1, 5),
                "observed_at": datetime.now(timezone.utc).isoformat(),
                "metadata": {"source": "edge-simulator", "model": "phase-1"},
            }

            try:
                response = await client.post(API_URL, json=payload)
                response.raise_for_status()
                event = response.json()
                print(f"sent {event_type:20} event={event['id']} confidence={payload['confidence']}")
            except httpx.HTTPError as exc:
                print(f"API unavailable: {exc}")

            await asyncio.sleep(2)


if __name__ == "__main__":
    asyncio.run(main())
