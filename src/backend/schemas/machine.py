from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.types import InferredStatus, MachineType


class MachineStatusResponse(BaseModel):
    """API schema describing a machine and its inferred status."""

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
                "latest_report_at": "2026-03-30T12:00:00Z",
                "has_reports": True,
            }
        },
    )
