from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum as SQLEnum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base
from backend.models.common import enum_values
from backend.types import MachineType

if TYPE_CHECKING:
    from backend.models.report import Report


class Machine(Base):
    """ORM model describing one laundry machine row."""

    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    type: Mapped[MachineType] = mapped_column(
        SQLEnum(
            MachineType,
            values_callable=enum_values,
            native_enum=False,
            name="machine_type",
        ),
        nullable=False,
    )
    reports: Mapped[list["Report"]] = relationship(
        back_populates="machine",
        cascade="all, delete-orphan",
    )
