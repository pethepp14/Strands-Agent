"""Mock banking tools for the card replacement demo.

Replace these implementations with authenticated, authorized, and audited bank
service calls before using this project outside a demonstration environment.
"""

from __future__ import annotations

from datetime import date, timedelta
import json
from pathlib import Path
from uuid import uuid4

from strands import tool


DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "mock_customers.json"


def load_mock_customers() -> dict[str, dict]:
    """Load the local synthetic dataset. No real customer information is used."""
    with DATA_FILE.open(encoding="utf-8") as data_file:
        dataset = json.load(data_file)
    return {customer["customer_id"]: customer for customer in dataset["customers"]}


CUSTOMERS = load_mock_customers()

AUTHENTICATED_CUSTOMERS: set[str] = set()


@tool
def authenticate_customer(customer_id: str, verification_session_id: str) -> dict:
    """Confirm authentication completed through the bank's secure verification service.

    Args:
        customer_id: The bank's internal customer identifier.
        verification_session_id: A reference from a completed secure verification flow.
            Never request or accept an OTP, password, PIN, CVV, or full card number.
    """
    if customer_id not in CUSTOMERS or not verification_session_id.startswith("verified-"):
        return {"authenticated": False, "message": "Secure verification could not be confirmed."}

    AUTHENTICATED_CUSTOMERS.add(customer_id)
    return {"authenticated": True, "customer_id": customer_id}


@tool
def list_customer_cards(customer_id: str) -> dict:
    """List the authenticated customer's eligible cards using masked card details only."""
    if customer_id not in AUTHENTICATED_CUSTOMERS:
        return {"error": "Authentication is required before viewing cards."}
    return {"cards": CUSTOMERS[customer_id]["cards"]}


@tool
def block_card(customer_id: str, card_id: str, reason: str) -> dict:
    """Immediately block an authenticated customer's lost or stolen card.

    Use only after the customer explicitly confirms blocking the selected card.
    """
    if customer_id not in AUTHENTICATED_CUSTOMERS:
        return {"error": "Authentication is required before blocking a card."}
    if reason.lower() not in {"lost", "stolen"}:
        return {"error": "Blocking through this flow is limited to lost or stolen cards."}

    for card in CUSTOMERS[customer_id]["cards"]:
        if card["card_id"] == card_id:
            card["status"] = "blocked"
            return {"blocked": True, "card_id": card_id}
    return {"error": "Card was not found for this customer."}


@tool
def check_replacement_eligibility(customer_id: str, card_id: str, reason: str) -> dict:
    """Check whether a card can be replaced and disclose mock replacement terms."""
    if customer_id not in AUTHENTICATED_CUSTOMERS:
        return {"eligible": False, "message": "Authentication is required."}
    if reason.lower() not in {"lost", "stolen", "damaged", "expired", "not_received"}:
        return {"eligible": False, "message": "This replacement reason is not supported."}
    if not any(card["card_id"] == card_id for card in CUSTOMERS[customer_id]["cards"]):
        return {"eligible": False, "message": "Card was not found for this customer."}

    return {
        "eligible": True,
        "replacement_fee": "0.00 USD",
        "delivery_estimate": "3-5 business days",
        "address": CUSTOMERS[customer_id]["registered_address"],
        "confirmation_required": True,
    }


@tool
def submit_replacement_request(customer_id: str, card_id: str, reason: str, customer_confirmed: bool) -> dict:
    """Submit a replacement only after authentication and explicit customer confirmation."""
    if customer_id not in AUTHENTICATED_CUSTOMERS:
        return {"error": "Authentication is required before submitting a replacement."}
    if not customer_confirmed:
        return {"error": "Explicit customer confirmation is required."}

    request_id = f"CR-{uuid4().hex[:8].upper()}"
    return {
        "submitted": True,
        "request_id": request_id,
        "card_id": card_id,
        "reason": reason.lower(),
        "estimated_delivery_date": str(date.today() + timedelta(days=5)),
    }


@tool
def transfer_to_human(customer_id: str, reason: str) -> dict:
    """Transfer a customer to a trained bank representative for an exception or concern."""
    return {"transferred": True, "customer_id": customer_id, "reason": reason}
