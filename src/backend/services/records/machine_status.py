from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from backend.domain.status_inference import infer_machine_status
from backend.services.clock import to_utc_datetime
from backend.types import InferredStatus, MachineType

if TYPE_CHECKING:
    from backend.domain.status_inference import ReportSnapshot
    from backend.models import Machine, Report


@dataclass(frozen=True, slots=True)
class MachineStatusRecord:
    """Service-layer record describing a machine and its status."""

    # Machine identity and display metadata.
    id: int
    name: str
    type: MachineType

    # Current inferred state and report presence.
    inferred_status: InferredStatus
    latest_report_at: datetime | None
    has_reports: bool

    @classmethod
    def from_sources(
        cls,
        machine: Machine,
        report: Report | None,
        *,
        snapshot: ReportSnapshot | None,
        now: datetime,
    ) -> MachineStatusRecord:
        """Build a status record from machine and report sources."""

        return cls(
            id=machine.id,
            name=machine.name,
            type=machine.type,
            inferred_status=infer_machine_status(snapshot, now),
            latest_report_at=to_utc_datetime(report.timestamp) if report else None,
            has_reports=report is not None,
        )
