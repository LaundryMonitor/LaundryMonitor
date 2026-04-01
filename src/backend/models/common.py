from backend.types import MachineType, ReportStatus


def enum_values(enum_cls: type[MachineType] | type[ReportStatus]) -> list[str]:
    """Return string enum values for SQLAlchemy enum columns."""

    return [enum_member.value for enum_member in enum_cls]
