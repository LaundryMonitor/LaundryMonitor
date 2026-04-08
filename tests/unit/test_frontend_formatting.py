from __future__ import annotations

from frontend.ui.formatting import format_timestamp


def test_format_timestamp_utc_to_local() -> None:
    """Verify UTC timestamps are converted to local timezone."""
    # Use a known UTC time with explicit offset
    utc_time = "2026-01-15T10:30:00+00:00"

    result = format_timestamp(utc_time)

    # Result should be a formatted string (exact time depends on system timezone)
    assert isinstance(result, str)
    assert "2026-01-15" in result
    # The hour should be converted (will vary by timezone)
    assert ":" in result  # Has time separator


def test_format_timestamp_with_z_suffix() -> None:
    """Verify timestamps with Z suffix (ISO format) are handled correctly."""
    # Z suffix indicates UTC
    utc_time = "2026-01-15T14:45:00Z"

    result = format_timestamp(utc_time)

    assert isinstance(result, str)
    assert "2026-01-15" in result


def test_format_timestamp_invalid_format_returns_original() -> None:
    """Verify invalid timestamps are returned unchanged."""
    invalid_time = "not-a-valid-timestamp"

    result = format_timestamp(invalid_time)

    assert result == invalid_time


def test_format_timestamp_returns_formatted_string() -> None:
    """Verify output format is YYYY-MM-DD HH:MM."""
    utc_time = "2026-03-30T08:15:00+00:00"

    result = format_timestamp(utc_time)

    # Should match pattern YYYY-MM-DD HH:MM
    assert len(result) == 16
    assert result[4] == "-"
    assert result[7] == "-"
    assert result[10] == " "
    assert result[13] == ":"


def test_format_timestamp_midnight_utc() -> None:
    """Verify midnight UTC is handled correctly."""
    midnight_utc = "2026-06-01T00:00:00+00:00"

    result = format_timestamp(midnight_utc)

    assert isinstance(result, str)
    assert "2026-06-01" in result
    # Hour should be converted based on local timezone (not 00:00 if not in UTC zone)
