def parse_optional_non_negative_int(raw_value: str) -> int | None:
    """Parse an optional non-negative integer from text input."""

    value = raw_value.strip()
    if not value:
        return None
    if not value.isdigit():
        raise ValueError("Time remaining must be a non-negative integer.")
    return int(value)
