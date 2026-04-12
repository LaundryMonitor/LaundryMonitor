from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING

from backend.services.clock import to_utc_datetime
from backend.types import ReportStatus

if TYPE_CHECKING:
    from backend.models import Report


@dataclass(frozen=True, slots=True)
class ReportRecord:
    """Service-layer record describing a stored machine report."""

    # Record identity and machine linkage.
    id: int
    machine_id: int

    # Reported status and optional remaining time.
    status: ReportStatus
    time_remaining: int | None

    # Optional reporter information and normalized timestamp.
    reporter_name: str | None
    timestamp: datetime

    @classmethod
    def from_model(cls, report: Report) -> ReportRecord:
        """Build a service record from a persisted report model."""

        return cls(
            id=report.id,
            machine_id=report.machine_id,
            status=report.status,
            time_remaining=report.time_remaining,
            reporter_name=report.reporter_name,
            timestamp=to_utc_datetime(report.timestamp),
        )
