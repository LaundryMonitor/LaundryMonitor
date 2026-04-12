"""Shared helper functions used by service command modules."""

from sqlalchemy.orm import Session

from backend.models import Machine
from backend.services.records import MachineNotFoundError


def require_machine(session: Session, machine_id: int) -> Machine:
    """Load a machine or raise a domain not-found error."""

    machine = session.get(Machine, machine_id)
    if machine is None:
        raise MachineNotFoundError(machine_id)
    return machine
