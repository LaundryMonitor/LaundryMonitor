from datetime import datetime, timezone


def to_utc_datetime(value: datetime) -> datetime:
    """Convert datetimes into timezone-aware UTC values."""

    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
