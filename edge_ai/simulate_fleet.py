"""Multi-bus city simulation for SIH demo.

Creates repeated observations around fixed hotspots so the backend can demonstrate
fleet correlation and confidence growth across independent buses.
"""

import asyncio
import random
from datetime import datetime, timezone

import httpx

API_URL = "http://127.0.0.1:8000/api/v1/events"

HOTSPOTS = [
    ("pothole", 17.38510, 78.48672, 4),
    ("road_damage", 17.38720, 78.48810, 3),
    ("waterlogging", 17.38380, 78.48490, 4),
    ("traffic_congestion", 17.38910, 78.49040, 5),
    ("pedestrian_risk", 17.38600, 78.48390, 4),
]


async def bus_worker(bus_no: int, client: httpx.AsyncClient) -> None:
    bus_id = f"HYD-BUS-{bus_no:03d}"
    camera_id = "front-01"

    while True:
        event_type, base_lat, base_lon, severity = random.choice(HOTSPOTS)
        payload = {
            "bus_id": bus_id,
            "camera_id": camera_id,
            "event_type": event_type,
            "location": {
                "latitude": base_lat + random.uniform(-0.00005, 0.00005),
                "longitude": base_lon + random.uniform(-0.00005, 0.00005),
            },
            "confidence": round(random.uniform(0.78, 0.98), 3),
            "severity": severity,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "source": "fleet-simulator",
                "edge_node": f"jetson-sim-{bus_no:03d}",
            },
        }

        try:
            response = await client.post(API_URL, json=payload)
            response.raise_for_status()
            print(f"{bus_id} -> {event_type:<20} {response.json()['id']}")
        except httpx.HTTPError as exc:
            print(f"{bus_id} API error: {exc}")

        await asyncio.sleep(random.uniform(1.5, 4.5))


async def main(bus_count: int = 6) -> None:
    async with httpx.AsyncClient(timeout=10) as client:
        await asyncio.gather(*(bus_worker(i + 1, client) for i in range(bus_count)))


if __name__ == "__main__":
    asyncio.run(main())
