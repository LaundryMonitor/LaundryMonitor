from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session, sessionmaker

from backend.models import Machine, Report
from backend.types import MachineType, ReportStatus


def test_post_valid_report(client, session_factory: sessionmaker[Session]) -> None:
    machine_id = _create_machine(session_factory, "Washer 1", MachineType.WASH)

    response = client.post(
        "/report",
        json={
            "machine_id": machine_id,
            "status": "busy",
            "time_remaining": 35,
            "reporter_name": "Polina",
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["machine_id"] == machine_id
    assert body["status"] == "busy"
    assert body["time_remaining"] == 35
    assert body["reporter_name"] == "Polina"
    assert "timestamp" in body


def test_post_report_invalid_machine_id(client) -> None:
    response = client.post(
        "/report",
        json={
            "machine_id": 9999,
            "status": "busy",
            "time_remaining": 20,
        },
    )

    assert response.status_code == 404


def test_post_report_invalid_status(client, session_factory: sessionmaker[Session]) -> None:
    machine_id = _create_machine(session_factory, "Washer 1", MachineType.WASH)

    response = client.post(
        "/report",
        json={
            "machine_id": machine_id,
            "status": "invalid",
            "time_remaining": 20,
        },
    )

    assert response.status_code == 422


def test_post_report_negative_time_remaining(
    client, session_factory: sessionmaker[Session]
) -> None:
    machine_id = _create_machine(session_factory, "Washer 1", MachineType.WASH)

    response = client.post(
        "/report",
        json={
            "machine_id": machine_id,
            "status": "busy",
            "time_remaining": -5,
        },
    )

    assert response.status_code == 422


def test_post_report_non_busy_time_remaining_is_ignored(
    client, session_factory: sessionmaker[Session]
) -> None:
    machine_id = _create_machine(session_factory, "Washer 1", MachineType.WASH)

    response = client.post(
        "/report",
        json={
            "machine_id": machine_id,
            "status": "free",
            "time_remaining": 25,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "free"
    assert body["time_remaining"] is None


def test_get_machines_with_inferred_statuses(
    client, session_factory: sessionmaker[Session]
) -> None:
    now = datetime.now(timezone.utc)

    washer_1_id = _create_machine(session_factory, "Washer 1", MachineType.WASH)
    washer_2_id = _create_machine(session_factory, "Washer 2", MachineType.WASH)
    dryer_1_id = _create_machine(session_factory, "Dryer 1", MachineType.DRY)
    dryer_2_id = _create_machine(session_factory, "Dryer 2", MachineType.DRY)

    _create_report(
        session_factory,
        machine_id=washer_1_id,
        status=ReportStatus.BUSY,
        timestamp=now - timedelta(minutes=5),
        time_remaining=25,
    )
    _create_report(
        session_factory,
        machine_id=dryer_1_id,
        status=ReportStatus.UNAVAILABLE,
        timestamp=now - timedelta(minutes=1),
        time_remaining=None,
    )
    _create_report(
        session_factory,
        machine_id=dryer_2_id,
        status=ReportStatus.BUSY,
        timestamp=now - timedelta(hours=5),
        time_remaining=None,
    )

    response = client.get("/machines")

    assert response.status_code == 200
    body = response.json()
    machines_by_id = {machine["id"]: machine for machine in body}

    assert machines_by_id[washer_1_id]["inferred_status"] == "busy"
    assert machines_by_id[washer_2_id]["inferred_status"] == "free"
    assert machines_by_id[washer_2_id]["has_reports"] is False
    assert machines_by_id[dryer_1_id]["inferred_status"] == "unavailable"
    assert machines_by_id[dryer_2_id]["inferred_status"] == "probably_free"


def test_get_machine_history(
    client, session_factory: sessionmaker[Session]
) -> None:
    now = datetime.now(timezone.utc)
    machine_id = _create_machine(session_factory, "Washer 1", MachineType.WASH)
    other_machine_id = _create_machine(session_factory, "Washer 2", MachineType.WASH)

    older_report_id = _create_report(
        session_factory,
        machine_id=machine_id,
        status=ReportStatus.BUSY,
        timestamp=now - timedelta(minutes=30),
        time_remaining=10,
    )
    newest_report_id = _create_report(
        session_factory,
        machine_id=machine_id,
        status=ReportStatus.FREE,
        timestamp=now - timedelta(minutes=5),
        time_remaining=None,
    )
    _create_report(
        session_factory,
        machine_id=other_machine_id,
        status=ReportStatus.BUSY,
        timestamp=now - timedelta(minutes=1),
        time_remaining=15,
    )

    response = client.get(f"/machines/{machine_id}/history?limit=2")

    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["id"] == newest_report_id
    assert body[1]["id"] == older_report_id
    assert all(report["machine_id"] == machine_id for report in body)


def test_get_machine_history_missing_machine(client) -> None:
    response = client.get("/machines/999/history")

    assert response.status_code == 404


def _create_machine(
    session_factory: sessionmaker[Session],
    name: str,
    machine_type: MachineType,
) -> int:
    with session_factory() as session:
        machine = Machine(name=name, type=machine_type)
        session.add(machine)
        session.commit()
        session.refresh(machine)
        return machine.id


def _create_report(
    session_factory: sessionmaker[Session],
    machine_id: int,
    status: ReportStatus,
    timestamp: datetime,
    time_remaining: int | None,
    reporter_name: str | None = None,
) -> int:
    with session_factory() as session:
        report = Report(
            machine_id=machine_id,
            status=status,
            timestamp=timestamp,
            time_remaining=time_remaining,
            reporter_name=reporter_name,
        )
        session.add(report)
        session.commit()
        session.refresh(report)
        return report.id
