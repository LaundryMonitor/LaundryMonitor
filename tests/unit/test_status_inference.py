from datetime import datetime, timedelta, timezone

from backend.domain.status_inference import ReportSnapshot, infer_machine_status
from backend.types import InferredStatus, ReportStatus


NOW = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)


def test_busy_with_known_time_not_expired() -> None:
    report = ReportSnapshot(
        status=ReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=5),
        time_remaining=10,
    )

    result = infer_machine_status(report, NOW)

    assert result == InferredStatus.BUSY


def test_busy_with_known_time_expired() -> None:
    report = ReportSnapshot(
        status=ReportStatus.BUSY,
        timestamp=NOW - timedelta(minutes=45),
        time_remaining=30,
    )

    result = infer_machine_status(report, NOW)

    assert result == InferredStatus.FREE


def test_busy_without_known_time_before_4_hours() -> None:
    report = ReportSnapshot(
        status=ReportStatus.BUSY,
        timestamp=NOW - timedelta(hours=3, minutes=30),
        time_remaining=None,
    )

    result = infer_machine_status(report, NOW)

    assert result == InferredStatus.BUSY


def test_busy_without_known_time_after_4_hours() -> None:
    report = ReportSnapshot(
        status=ReportStatus.BUSY,
        timestamp=NOW - timedelta(hours=4),
        time_remaining=None,
    )

    result = infer_machine_status(report, NOW)

    assert result == InferredStatus.PROBABLY_FREE


def test_unavailable_latest_report() -> None:
    report = ReportSnapshot(
        status=ReportStatus.UNAVAILABLE,
        timestamp=NOW - timedelta(minutes=1),
        time_remaining=None,
    )

    result = infer_machine_status(report, NOW)

    assert result == InferredStatus.UNAVAILABLE


def test_explicit_free_latest_report() -> None:
    report = ReportSnapshot(
        status=ReportStatus.FREE,
        timestamp=NOW - timedelta(minutes=1),
        time_remaining=None,
    )

    result = infer_machine_status(report, NOW)

    assert result == InferredStatus.FREE


def test_no_reports_defaults_to_free() -> None:
    result = infer_machine_status(None, NOW)

    assert result == InferredStatus.FREE
