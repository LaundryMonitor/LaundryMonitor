from pydantic import BaseModel, ConfigDict, Field

from backend.types import ReportStatus


class ReportCreateRequest(BaseModel):
    """API schema used when submitting a machine report."""

    machine_id: int = Field(gt=0, description="Existing machine ID.")
    status: ReportStatus
    time_remaining: int | None = Field(
        default=None,
        gt=0,
        le=1440,
        description=(
            "Remaining minutes. Used only when status is 'busy'. "
            "For other statuses it is accepted but stored as null. "
            "Must be between 1 and 1440."
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
