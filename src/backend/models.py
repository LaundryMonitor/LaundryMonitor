from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.types import MachineType, ReportStatus


def _enum_values(enum_cls: type[MachineType] | type[ReportStatus]) -> list[str]:
    return [enum_member.value for enum_member in enum_cls]


class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    type: Mapped[MachineType] = mapped_column(
        SQLEnum(
            MachineType,
            values_callable=_enum_values,
            native_enum=False,
            name="machine_type",
        ),
        nullable=False,
    )

    reports: Mapped[list["Report"]] = relationship(
        back_populates="machine",
        cascade="all, delete-orphan",
    )


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (Index("ix_reports_machine_id_timestamp", "machine_id", "timestamp"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    machine_id: Mapped[int] = mapped_column(ForeignKey("machines.id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    status: Mapped[ReportStatus] = mapped_column(
        SQLEnum(
            ReportStatus,
            values_callable=_enum_values,
            native_enum=False,
            name="report_status",
        ),
        nullable=False,
    )
    time_remaining: Mapped[int | None] = mapped_column(Integer, nullable=True)
    reporter_name: Mapped[str | None] = mapped_column(String(100), nullable=True)

    machine: Mapped[Machine] = relationship(back_populates="reports")
