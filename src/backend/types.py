from enum import Enum


class MachineType(str, Enum):
    """Enum of supported laundry machine types."""

    WASH = "wash"
    DRY = "dry"


class ReportStatus(str, Enum):
    """Enum of raw statuses submitted by users."""

    BUSY = "busy"
    FREE = "free"
    UNAVAILABLE = "unavailable"


class InferredStatus(str, Enum):
    """Enum of statuses inferred by backend rules."""

    BUSY = "busy"
    FREE = "free"
    UNAVAILABLE = "unavailable"
    PROBABLY_FREE = "probably_free"
