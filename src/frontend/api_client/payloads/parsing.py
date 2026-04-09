def parse_optional_non_negative_int(raw_value: str) -> int | None:
    """Parse an optional positive integer from text input."""

    value = raw_value.strip()
    if not value:
        return None
    if not value.isdigit():
        raise ValueError("Time remaining must be a positive integer.")

    int_value = int(value)
    if int_value > 1440:
        raise ValueError("Time remaining must be less than a 1440 minutes (24 hours)")
    if int_value == 0:
        raise ValueError("Time remaining must be positive integer")

    return int_value
