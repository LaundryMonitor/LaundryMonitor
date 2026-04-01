class MachineNotFoundError(Exception):
    """Raised when a requested machine record does not exist."""

    def __init__(self, machine_id: int) -> None:
        """Store the missing machine identifier on the exception."""

        self.machine_id = machine_id
        super().__init__(f"Machine {machine_id} was not found")
