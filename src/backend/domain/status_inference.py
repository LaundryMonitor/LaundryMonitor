from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from backend.types import InferredStatus, ReportStatus


BUSY_WITHOUT_TIME_WINDOW = timedelta(hours=4)


@dataclass(frozen=True, slots=True)
class ReportSnapshot:
    status: ReportStatus
    timestamp: datetime
    time_remaining: int | None


def infer_machine_status(
    latest_report: ReportSnapshot | None,
    now: datetime,
) -> InferredStatus:
    """
    Infer a machine status from its latest report.

    Behavior for machines with no reports: treat as FREE.
    This keeps first-time usage simple and avoids blocking users with "unknown."
    """
    if latest_report is None:
        return InferredStatus.FREE

    if latest_report.status == ReportStatus.UNAVAILABLE:
        return InferredStatus.UNAVAILABLE

    if latest_report.status == ReportStatus.FREE:
        return InferredStatus.FREE

    return _infer_from_busy_report(latest_report, now)


def _infer_from_busy_report(report: ReportSnapshot, now: datetime) -> InferredStatus:
    if report.time_remaining is None:
        stale_busy_cutoff = report.timestamp + BUSY_WITHOUT_TIME_WINDOW
        if now < stale_busy_cutoff:
            return InferredStatus.BUSY
        return InferredStatus.PROBABLY_FREE

    busy_until = report.timestamp + timedelta(minutes=report.time_remaining)
    if now < busy_until:
        return InferredStatus.BUSY
    return InferredStatus.FREE
