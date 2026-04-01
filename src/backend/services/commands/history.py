from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.models import Report
from backend.services.commands.common import require_machine
from backend.services.records import ReportRecord


def get_machine_history(
    session: Session,
    machine_id: int,
    *,
    limit: int = 20,
) -> list[ReportRecord]:
    """Return recent reports for one machine, newest first."""

    require_machine(session, machine_id)
    reports = session.scalars(
        select(Report)
        .where(Report.machine_id == machine_id)
        .order_by(desc(Report.timestamp), desc(Report.id))
        .limit(limit)
    ).all()
    return [ReportRecord.from_model(report) for report in reports]
