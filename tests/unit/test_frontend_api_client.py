import pytest

from frontend.api_client import build_report_payload, parse_optional_non_negative_int
from frontend.config import DEFAULT_BACKEND_URL, get_backend_base_url


def test_build_report_payload_for_busy_with_time_remaining() -> None:
    payload = build_report_payload(
        machine_id=2,
        status="busy",
        time_remaining_text="35",
        reporter_name_text=" Polina ",
    )

    assert payload == {
        "machine_id": 2,
        "status": "busy",
        "time_remaining": 35,
        "reporter_name": "Polina",
    }


def test_build_report_payload_ignores_time_for_non_busy_status() -> None:
    payload = build_report_payload(
        machine_id=1,
        status="free",
        time_remaining_text="25",
        reporter_name_text="",
    )

    assert payload == {
        "machine_id": 1,
        "status": "free",
    }


def test_build_report_payload_rejects_invalid_status() -> None:
    with pytest.raises(ValueError):
        build_report_payload(
            machine_id=1,
            status="invalid",
            time_remaining_text="",
            reporter_name_text="",
        )


def test_parse_optional_non_negative_int() -> None:
    assert parse_optional_non_negative_int("") is None
    assert parse_optional_non_negative_int("12") == 12

    with pytest.raises(ValueError):
        parse_optional_non_negative_int("-1")

    with pytest.raises(ValueError):
        parse_optional_non_negative_int("abc")


def test_get_backend_base_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("LAUNDRY_MONITOR_API_URL", raising=False)
    assert get_backend_base_url() == DEFAULT_BACKEND_URL

    monkeypatch.setenv("LAUNDRY_MONITOR_API_URL", "http://backend:9000/")
    assert get_backend_base_url() == "http://backend:9000"
