"""Database access functions for synthetic card-replacement demo data."""

from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3


PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATABASE_FILE = PROJECT_ROOT / "data" / "card_replacement.db"
SEED_FILE = PROJECT_ROOT / "data" / "mock_customers.json"


def _connect() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            registered_address TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS cards (
            card_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL REFERENCES customers(customer_id),
            card_type TEXT NOT NULL CHECK(card_type IN ('credit', 'debit')),
            network TEXT NOT NULL,
            last_four TEXT NOT NULL,
            status TEXT NOT NULL CHECK(status IN ('active', 'blocked'))
        );

        CREATE TABLE IF NOT EXISTS replacement_requests (
            request_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL REFERENCES customers(customer_id),
            card_id TEXT NOT NULL REFERENCES cards(card_id),
            reason TEXT NOT NULL,
            status TEXT NOT NULL,
            replacement_fee TEXT NOT NULL,
            estimated_delivery_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS audit_events (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id TEXT,
            event_type TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_cards_customer_id ON cards(customer_id);
        CREATE INDEX IF NOT EXISTS idx_requests_customer_id ON replacement_requests(customer_id);
        CREATE INDEX IF NOT EXISTS idx_audit_customer_id ON audit_events(customer_id);
        """
    )


def _seed_database(connection: sqlite3.Connection) -> None:
    dataset = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    customers = dataset["customers"]
    connection.executemany(
        """
        INSERT INTO customers (customer_id, display_name, registered_address)
        VALUES (:customer_id, :display_name, :registered_address)
        """,
        customers,
    )
    cards = [
        {
            "card_id": card["card_id"],
            "customer_id": customer["customer_id"],
            "card_type": card["type"],
            "network": card["network"],
            "last_four": card["last_four"],
            "status": card["status"],
        }
        for customer in customers
        for card in customer["cards"]
    ]
    connection.executemany(
        """
        INSERT INTO cards (card_id, customer_id, card_type, network, last_four, status)
        VALUES (:card_id, :customer_id, :card_type, :network, :last_four, :status)
        """,
        cards,
    )


def initialize_database() -> None:
    """Create the schema and seed it only when the local database is empty."""
    with _connect() as connection:
        _create_schema(connection)
        customer_count = connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0]
        if customer_count == 0:
            _seed_database(connection)


def reset_database() -> None:
    """Reset the local database to the original synthetic dataset."""
    with _connect() as connection:
        _create_schema(connection)
        connection.execute("DELETE FROM audit_events")
        connection.execute("DELETE FROM replacement_requests")
        connection.execute("DELETE FROM cards")
        connection.execute("DELETE FROM customers")
        _seed_database(connection)


def customer_exists(customer_id: str) -> bool:
    with _connect() as connection:
        return connection.execute(
            "SELECT EXISTS(SELECT 1 FROM customers WHERE customer_id = ?)", (customer_id,)
        ).fetchone()[0] == 1


def list_cards(customer_id: str) -> list[dict]:
    with _connect() as connection:
        rows = connection.execute(
            """
            SELECT card_id, card_type AS type, network, last_four, status
            FROM cards
            WHERE customer_id = ?
            ORDER BY card_type
            """,
            (customer_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def card_exists_for_customer(customer_id: str, card_id: str) -> bool:
    with _connect() as connection:
        return connection.execute(
            "SELECT EXISTS(SELECT 1 FROM cards WHERE customer_id = ? AND card_id = ?)",
            (customer_id, card_id),
        ).fetchone()[0] == 1


def registered_address(customer_id: str) -> str | None:
    with _connect() as connection:
        row = connection.execute(
            "SELECT registered_address FROM customers WHERE customer_id = ?", (customer_id,)
        ).fetchone()
    return row["registered_address"] if row else None


def log_event(customer_id: str | None, event_type: str, details: dict) -> None:
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO audit_events (customer_id, event_type, details, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (
                customer_id,
                event_type,
                json.dumps(details, sort_keys=True),
                datetime.now(timezone.utc).isoformat(),
            ),
        )


def block_customer_card(customer_id: str, card_id: str, reason: str) -> bool:
    with _connect() as connection:
        result = connection.execute(
            """
            UPDATE cards
            SET status = 'blocked'
            WHERE customer_id = ? AND card_id = ? AND status = 'active'
            """,
            (customer_id, card_id),
        )
        if result.rowcount != 1:
            return False
        connection.execute(
            """
            INSERT INTO audit_events (customer_id, event_type, details, created_at)
            VALUES (?, 'card_blocked', ?, ?)
            """,
            (
                customer_id,
                json.dumps({"card_id": card_id, "reason": reason}),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
    return True


def create_replacement_request(
    request_id: str,
    customer_id: str,
    card_id: str,
    reason: str,
    replacement_fee: str,
    estimated_delivery_date: str,
) -> None:
    with _connect() as connection:
        connection.execute(
            """
            INSERT INTO replacement_requests (
                request_id, customer_id, card_id, reason, status, replacement_fee,
                estimated_delivery_date, created_at
            ) VALUES (?, ?, ?, ?, 'submitted', ?, ?, ?)
            """,
            (
                request_id,
                customer_id,
                card_id,
                reason,
                replacement_fee,
                estimated_delivery_date,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        connection.execute(
            """
            INSERT INTO audit_events (customer_id, event_type, details, created_at)
            VALUES (?, 'replacement_submitted', ?, ?)
            """,
            (
                customer_id,
                json.dumps({"request_id": request_id, "card_id": card_id, "reason": reason}),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
