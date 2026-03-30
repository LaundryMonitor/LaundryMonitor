from __future__ import annotations

import os
from typing import Any

from locust import HttpUser, between, task


DEFAULT_HOST = "http://127.0.0.1:8000"


class LaundrySmokeUser(HttpUser):
    wait_time = between(0.5, 1.0)
    host = os.getenv("LAUNDRY_MONITOR_API_URL", DEFAULT_HOST)

    @task(3)
    def get_machines(self) -> None:
        self.client.get("/machines", name="GET /machines")

    @task(1)
    def post_report(self) -> None:
        response = self.client.get("/machines", name="GET /machines (for report)")
        if response.status_code != 200:
            return

        machines = _safe_json(response)
        if not machines:
            return

        first_machine = machines[0]
        machine_id = first_machine.get("id")
        if not isinstance(machine_id, int):
            return

        payload = {
            "machine_id": machine_id,
            "status": "busy",
            "time_remaining": 5,
            "reporter_name": "locust",
        }
        self.client.post("/report", json=payload, name="POST /report")


def _safe_json(response) -> list[dict[str, Any]]:
    try:
        data = response.json()
    except ValueError:
        return []
    return data if isinstance(data, list) else []
