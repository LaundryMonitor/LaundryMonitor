from datetime import datetime, timezone

from sqlalchemy.orm import Session

from backend.models import Report
from backend.schemas import ReportCreateRequest
from backend.services.commands.common import require_machine
from backend.services.records import ReportRecord, InvalidTimeRemainingError
from backend.types import ReportStatus


def normalize_time_remaining(status: ReportStatus, time_remaining: int | None) -> int | None:
    """Keep remaining time only for reports marked as busy."""

    if status != ReportStatus.BUSY:
        return None

    if 0 < time_remaining <= 1440:
        return time_remaining

    raise InvalidTimeRemainingError(time_remaining)


def create_report(session: Session, payload: ReportCreateRequest) -> ReportRecord:
    """Create a report row and return its service record."""

    require_machine(session, payload.machine_id)
    normalized_time_remaining = normalize_time_remaining(payload.status, payload.time_remaining)
    report = Report(
        machine_id=payload.machine_id,
        status=payload.status,
        time_remaining=normalized_time_remaining,
        reporter_name=payload.reporter_name,
        timestamp=datetime.now(timezone.utc),
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    return ReportRecord.from_model(report)
