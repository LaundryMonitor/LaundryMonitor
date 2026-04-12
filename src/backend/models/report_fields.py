from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.models.common import enum_values
from backend.types import ReportStatus


REPORT_INDEX = Index("ix_reports_machine_id_timestamp", "machine_id", "timestamp")


def report_timestamp_default() -> datetime:
    """Return the default UTC timestamp for new reports."""

    return datetime.now(timezone.utc)


def report_machine_id_column() -> Mapped[int]:
    """Build the foreign-key column linking reports to machines."""

    return mapped_column(
        ForeignKey("machines.id", ondelete="CASCADE"),
        nullable=False,
    )


def report_timestamp_column():
    """Build the timestamp column used by report rows."""

    return mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=report_timestamp_default,
    )


def report_status_column() -> Mapped[ReportStatus]:
    """Build the enum status column stored on reports."""

    return mapped_column(
        SQLEnum(
            ReportStatus,
            values_callable=enum_values,
            native_enum=False,
            name="report_status",
        ),
        nullable=False,
    )


def report_time_remaining_column():
    """Build the optional remaining-minutes column for reports."""

    return mapped_column(Integer, nullable=True)


def report_reporter_name_column():
    """Build the optional reporter-name column for reports."""

    return mapped_column(String(100), nullable=True)


def report_machine_relationship():
    """Build the ORM relationship from reports to machines."""

    return relationship(back_populates="reports")
