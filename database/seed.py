"""Initialize or reset the local synthetic SQLite database."""

from __future__ import annotations

import argparse

from .repository import DATABASE_FILE, initialize_database, reset_database


def main() -> None:
    parser = argparse.ArgumentParser(description="Initialize the card replacement demo database.")
    parser.add_argument("--reset", action="store_true", help="Reset synthetic data and remove demo actions.")
    arguments = parser.parse_args()

    if arguments.reset:
        reset_database()
        action = "Reset"
    else:
        initialize_database()
        action = "Initialized"
    print(f"{action} SQLite demo database at {DATABASE_FILE}")


if __name__ == "__main__":
    main()
