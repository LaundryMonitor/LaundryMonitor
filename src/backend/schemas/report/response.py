from datetime import datetime

from pydantic import BaseModel, ConfigDict

from backend.types import ReportStatus


# Example response shown in generated OpenAPI documentation.
REPORT_RESPONSE_EXAMPLE = {
    "id": 1,
    "machine_id": 2,
    "status": "busy",
    "time_remaining": 35,
    "reporter_name": "Polina",
    "timestamp": "2026-03-30T12:00:00Z",
}


class ReportResponse(BaseModel):
    """API schema representing a stored machine report."""

    id: int
    machine_id: int
    status: ReportStatus
    time_remaining: int | None
    reporter_name: str | None
    timestamp: datetime

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={"example": REPORT_RESPONSE_EXAMPLE},
    )
