"""SQLite persistence layer for the local card replacement demo."""

from .repository import initialize_database

__all__ = ["initialize_database"]
