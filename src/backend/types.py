from enum import Enum


class MachineType(str, Enum):
    WASH = "wash"
    DRY = "dry"


class ReportStatus(str, Enum):
    BUSY = "busy"
    FREE = "free"
    UNAVAILABLE = "unavailable"


class InferredStatus(str, Enum):
    BUSY = "busy"
    FREE = "free"
    UNAVAILABLE = "unavailable"
    PROBABLY_FREE = "probably_free"
