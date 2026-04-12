from __future__ import annotations

from typing import TYPE_CHECKING

from datetime import datetime

from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models.report_fields import (
    REPORT_INDEX,
    report_machine_id_column,
    report_machine_relationship,
    report_reporter_name_column,
    report_status_column,
    report_time_remaining_column,
    report_timestamp_column,
)
from backend.types import ReportStatus

if TYPE_CHECKING:
    from backend.models.machine import Machine


class Report(Base):
    """ORM model describing one submitted machine report."""

    __tablename__ = "reports"
    __table_args__ = (REPORT_INDEX,)

    # Row identity and machine linkage.
    id: Mapped[int] = mapped_column(primary_key=True)
    machine_id: Mapped[int] = report_machine_id_column()

    # Reported timing and status values.
    timestamp: Mapped[datetime] = report_timestamp_column()
    status: Mapped[ReportStatus] = report_status_column()

    # Optional user-provided context.
    time_remaining: Mapped[int | None] = report_time_remaining_column()
    reporter_name: Mapped[str | None] = report_reporter_name_column()

    # ORM back-reference to the owning machine.
    machine: Mapped["Machine"] = report_machine_relationship()
