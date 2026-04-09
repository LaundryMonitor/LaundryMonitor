class MachineNotFoundError(Exception):
    """Raised when a requested machine record does not exist."""

    def __init__(self, machine_id: int) -> None:
        """Store the missing machine identifier on the exception."""

        self.machine_id = machine_id
        super().__init__(f"Machine {machine_id} was not found")


class InvalidTimeRemainingError(Exception):
    """Raised when a requested remaining_time is not in interval (0, 1440]"""

    def __init__(self, time: int) -> None:
        self.remaining_time = time
        super().__init__(f"Remaining time value ({time}) is out of bounds: (0, 1440]")