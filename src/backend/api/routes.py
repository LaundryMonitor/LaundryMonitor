from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.schemas import MachineStatusResponse, ReportCreateRequest, ReportResponse
from backend.services import (
    MachineNotFoundError,
    ReportRecord,
    create_report,
    get_machine_history,
    list_machines_with_status,
)


router = APIRouter()


@router.post(
    "/report",
    response_model=ReportResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Reports"],
    summary="Submit a machine report",
    description=(
        "Create a new machine report with the current server timestamp. "
        "If status is `free` or `unavailable`, `time_remaining` is ignored and stored as null."
    ),
)
async def post_report(
    payload: ReportCreateRequest,
    session: Annotated[Session, Depends(get_db)],
) -> ReportResponse:
    """Store a new machine report submitted by a user."""

    try:
        report = create_report(session, payload)
    except MachineNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine {exc.machine_id} not found",
        ) from exc

    return _to_report_response(report)


@router.get(
    "/machines",
    response_model=list[MachineStatusResponse],
    tags=["Machines"],
    summary="List machines with inferred status",
    description=(
        "Return all machines and their inferred current status based on the latest report "
        "and backend status inference rules."
    ),
)
async def get_machines(
    session: Annotated[Session, Depends(get_db)],
) -> list[MachineStatusResponse]:
    """Return all machines with inferred current statuses."""

    machines = list_machines_with_status(session)
    return [MachineStatusResponse.model_validate(machine) for machine in machines]


@router.get(
    "/machines/{machine_id}/history",
    response_model=list[ReportResponse],
    tags=["Machines"],
    summary="Get recent report history for a machine",
    description="Return recent reports for one machine, newest first.",
)
async def get_machine_report_history(
    machine_id: Annotated[int, Path(gt=0, description="Machine ID.")],
    session: Annotated[Session, Depends(get_db)],
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[ReportResponse]:
    """Return recent reports for one machine."""

    try:
        reports = get_machine_history(session, machine_id, limit=limit)
    except MachineNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Machine {exc.machine_id} not found",
        ) from exc

    return [_to_report_response(report) for report in reports]


def _to_report_response(report: ReportRecord) -> ReportResponse:
    """Convert a service-layer record into an API response."""

    return ReportResponse.model_validate(report)
