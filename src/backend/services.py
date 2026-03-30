from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from backend.domain.status_inference import ReportSnapshot, infer_machine_status
from backend.models import Machine, Report
from backend.schemas import ReportCreateRequest
from backend.types import InferredStatus, MachineType, ReportStatus


class MachineNotFoundError(Exception):
    def __init__(self, machine_id: int) -> None:
        self.machine_id = machine_id
        super().__init__(f"Machine {machine_id} was not found")


@dataclass(frozen=True, slots=True)
class ReportRecord:
    id: int
    machine_id: int
    status: ReportStatus
    time_remaining: int | None
    reporter_name: str | None
    timestamp: datetime


@dataclass(frozen=True, slots=True)
class MachineStatusRecord:
    id: int
    name: str
    type: MachineType
    inferred_status: InferredStatus
    latest_report_at: datetime | None
    has_reports: bool


def create_report(session: Session, payload: ReportCreateRequest) -> ReportRecord:
    _require_machine(session, payload.machine_id)
    normalized_time_remaining = _normalize_time_remaining(payload.status, payload.time_remaining)

    report = Report(
        machine_id=payload.machine_id,
        status=payload.status,
        time_remaining=normalized_time_remaining,
        reporter_name=payload.reporter_name,
        timestamp=datetime.now(timezone.utc),
    )
    session.add(report)
    session.commit()
    session.refresh(report)
    return _to_report_record(report)


def list_machines_with_status(session: Session, *, now: datetime | None = None) -> list[MachineStatusRecord]:
    effective_now = _to_utc_datetime(now or datetime.now(timezone.utc))
    machines = session.scalars(select(Machine).order_by(Machine.id)).all()
    machine_statuses: list[MachineStatusRecord] = []

    for machine in machines:
        latest_report = _get_latest_report_for_machine(session, machine.id)
        latest_report_at = _to_utc_datetime(latest_report.timestamp) if latest_report else None
        report_snapshot = _to_report_snapshot(latest_report)
        inferred_status = infer_machine_status(report_snapshot, effective_now)

        machine_statuses.append(
            MachineStatusRecord(
                id=machine.id,
                name=machine.name,
                type=machine.type,
                inferred_status=inferred_status,
                latest_report_at=latest_report_at,
                has_reports=latest_report is not None,
            )
        )

    return machine_statuses


def get_machine_history(session: Session, machine_id: int, *, limit: int = 20) -> list[ReportRecord]:
    _require_machine(session, machine_id)
    reports = session.scalars(
        select(Report)
        .where(Report.machine_id == machine_id)
        .order_by(desc(Report.timestamp), desc(Report.id))
        .limit(limit)
    ).all()
    return [_to_report_record(report) for report in reports]


def _require_machine(session: Session, machine_id: int) -> Machine:
    machine = session.get(Machine, machine_id)
    if machine is None:
        raise MachineNotFoundError(machine_id)
    return machine


def _normalize_time_remaining(status: ReportStatus, time_remaining: int | None) -> int | None:
    if status != ReportStatus.BUSY:
        return None
    return time_remaining


def _to_report_snapshot(report: Report | None) -> ReportSnapshot | None:
    if report is None:
        return None
    return ReportSnapshot(
        status=report.status,
        timestamp=_to_utc_datetime(report.timestamp),
        time_remaining=report.time_remaining,
    )


def _to_report_record(report: Report) -> ReportRecord:
    return ReportRecord(
        id=report.id,
        machine_id=report.machine_id,
        status=report.status,
        time_remaining=report.time_remaining,
        reporter_name=report.reporter_name,
        timestamp=_to_utc_datetime(report.timestamp),
    )


def _get_latest_report_for_machine(session: Session, machine_id: int) -> Report | None:
    return session.scalar(
        select(Report)
        .where(Report.machine_id == machine_id)
        .order_by(desc(Report.timestamp), desc(Report.id))
        .limit(1)
    )


def _to_utc_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)
