from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models import Machine
from backend.services.clock import to_utc_datetime
from backend.services.queries.helpers import get_latest_report_for_machine, to_report_snapshot
from backend.services.records import MachineStatusRecord


def list_machines_with_status(
    session: Session,
    *,
    now: datetime | None = None,
) -> list[MachineStatusRecord]:
    """List machines with statuses inferred from recent reports."""

    effective_now = to_utc_datetime(now or datetime.now(timezone.utc))
    machines = session.scalars(select(Machine).order_by(Machine.id)).all()
    statuses: list[MachineStatusRecord] = []

    for machine in machines:
        latest_report = get_latest_report_for_machine(session, machine.id)
        statuses.append(
            MachineStatusRecord.from_sources(
                machine,
                latest_report,
                snapshot=to_report_snapshot(latest_report),
                now=effective_now,
            )
        )

    return statuses
