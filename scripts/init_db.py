from backend.database import init_database


def main() -> None:
    """Initialize database tables using the configured project settings."""

    init_database()
    print("Database initialized.")


if __name__ == "__main__":
    main()
