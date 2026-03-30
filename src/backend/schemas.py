from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from backend.types import InferredStatus, MachineType, ReportStatus


class ReportCreateRequest(BaseModel):
    machine_id: int = Field(gt=0, description="Existing machine ID.")
    status: ReportStatus
    time_remaining: int | None = Field(
        default=None,
        ge=0,
        description=(
            "Remaining minutes. Used only when status is 'busy'. "
            "For other statuses it is accepted but stored as null."
        ),
    )
    reporter_name: str | None = Field(default=None, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "machine_id": 2,
                "status": "busy",
                "time_remaining": 35,
                "reporter_name": "Polina",
            }
        }
    )


class ReportResponse(BaseModel):
    id: int
    machine_id: int
    status: ReportStatus
    time_remaining: int | None
    reporter_name: str | None
    timestamp: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "machine_id": 2,
                "status": "busy",
                "time_remaining": 35,
                "reporter_name": "Polina",
                "timestamp": "2026-03-30T12:00:00Z",
            }
        },
    )


class MachineStatusResponse(BaseModel):
    id: int
    name: str
    type: MachineType
    inferred_status: InferredStatus
    latest_report_at: datetime | None
    has_reports: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "name": "Washer 1",
                "type": "wash",
                "inferred_status": "free",
                "latest_report_at": "2026-03-30T11:40:00Z",
                "has_reports": True,
            }
        },
    )
