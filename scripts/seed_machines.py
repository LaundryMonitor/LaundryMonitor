from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from backend.database import SessionLocal, init_database
from backend.models import Machine
from backend.types import MachineType


DEFAULT_MACHINES: tuple[tuple[str, MachineType], ...] = (
    ("Washer 1", MachineType.WASH),
    ("Washer 2", MachineType.WASH),
    ("Washer 3", MachineType.WASH),
    ("Washer 4", MachineType.WASH),
    ("Dryer 1", MachineType.DRY),
    ("Dryer 2", MachineType.DRY),
    ("Dryer 3", MachineType.DRY),
    ("Dryer 4", MachineType.DRY),
)


def seed_machines(session: Session, machine_specs: Sequence[tuple[str, MachineType]]) -> int:
    """Insert missing machine records without creating duplicates."""

    existing_names = set(session.scalars(select(Machine.name)))
    created_count = 0

    for machine_name, machine_type in machine_specs:
        if machine_name in existing_names:
            continue
        session.add(Machine(name=machine_name, type=machine_type))
        created_count += 1

    if created_count:
        session.commit()

    return created_count


def main() -> None:
    """Initialize storage and seed the default machine list."""

    init_database()
    with SessionLocal() as session:
        created_count = seed_machines(session, DEFAULT_MACHINES)
        total_count = session.scalar(select(func.count(Machine.id))) or 0

    print(f"Machines created: {created_count}")
    print(f"Total machines in DB: {total_count}")


if __name__ == "__main__":
    main()
