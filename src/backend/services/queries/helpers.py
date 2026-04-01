from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.domain.status_inference import ReportSnapshot
from backend.models import Report
from backend.services.clock import to_utc_datetime


def get_latest_report_for_machine(session: Session, machine_id: int) -> Report | None:
    """Return the newest stored report for one machine."""

    return session.scalar(
        select(Report)
        .where(Report.machine_id == machine_id)
        .order_by(desc(Report.timestamp), desc(Report.id))
        .limit(1)
    )


def to_report_snapshot(report: Report | None) -> ReportSnapshot | None:
    """Convert a report row into an inference snapshot."""

    if report is None:
        return None
    return ReportSnapshot(
        status=report.status,
        timestamp=to_utc_datetime(report.timestamp),
        time_remaining=report.time_remaining,
    )
