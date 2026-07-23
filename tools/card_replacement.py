"""Mock banking tools for the card replacement demo.

Replace these implementations with authenticated, authorized, and audited bank
service calls before using this project outside a demonstration environment.
"""

from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from database.repository import (
    block_customer_card,
    card_exists_for_customer,
    create_replacement_request,
    customer_exists,
    initialize_database,
    list_cards,
    log_event,
    registered_address,
)
from strands import tool


initialize_database()

AUTHENTICATED_CUSTOMERS: set[str] = set()
SUPPORTED_REASONS = {"lost", "stolen", "damaged", "expired", "not_received"}


@tool
def authenticate_customer(customer_id: str, verification_session_id: str) -> dict:
    """Confirm authentication completed through the bank's secure verification service.

    Args:
        customer_id: The bank's internal customer identifier.
        verification_session_id: A reference from a completed secure verification flow.
            Never request or accept an OTP, password, PIN, CVV, or full card number.
    """
    if not customer_exists(customer_id) or not verification_session_id.startswith("verified-"):
        log_event(customer_id, "authentication_failed", {"verification_session_id": "redacted"})
        return {"authenticated": False, "message": "Secure verification could not be confirmed."}

    AUTHENTICATED_CUSTOMERS.add(customer_id)
    log_event(customer_id, "authenticated", {"method": "demo_verification_session"})
    return {"authenticated": True, "customer_id": customer_id}


@tool
def list_customer_cards(customer_id: str) -> dict:
    """List the authenticated customer's eligible cards using masked card details only."""
    if customer_id not in AUTHENTICATED_CUSTOMERS:
        return {"error": "Authentication is required before viewing cards."}
    return {"cards": list_cards(customer_id)}


@tool
def block_card(customer_id: str, card_id: str, reason: str) -> dict:
    """Immediately block an authenticated customer's lost or stolen card.

    Use only after the customer explicitly confirms blocking the selected card.
    """
    if customer_id not in AUTHENTICATED_CUSTOMERS:
        return {"error": "Authentication is required before blocking a card."}
    if reason.lower() not in {"lost", "stolen"}:
        return {"error": "Blocking through this flow is limited to lost or stolen cards."}
    if block_customer_card(customer_id, card_id, reason.lower()):
        return {"blocked": True, "card_id": card_id}
    return {"error": "Card was not found or is already blocked."}


@tool
def check_replacement_eligibility(customer_id: str, card_id: str, reason: str) -> dict:
    """Check whether a card can be replaced and disclose mock replacement terms."""
    if customer_id not in AUTHENTICATED_CUSTOMERS:
        return {"eligible": False, "message": "Authentication is required."}
    if reason.lower() not in SUPPORTED_REASONS:
        return {"eligible": False, "message": "This replacement reason is not supported."}
    if not card_exists_for_customer(customer_id, card_id):
        return {"eligible": False, "message": "Card was not found for this customer."}

    return {
        "eligible": True,
        "replacement_fee": "0.00 USD",
        "delivery_estimate": "3-5 business days",
        "address": registered_address(customer_id),
        "confirmation_required": True,
    }


@tool
def submit_replacement_request(customer_id: str, card_id: str, reason: str, customer_confirmed: bool) -> dict:
    """Submit a replacement only after authentication and explicit customer confirmation."""
    if customer_id not in AUTHENTICATED_CUSTOMERS:
        return {"error": "Authentication is required before submitting a replacement."}
    if not customer_confirmed:
        return {"error": "Explicit customer confirmation is required."}
    if reason.lower() not in SUPPORTED_REASONS or not card_exists_for_customer(customer_id, card_id):
        return {"error": "The selected card or replacement reason is not valid."}

    request_id = f"CR-{uuid4().hex[:8].upper()}"
    estimated_delivery_date = str(date.today() + timedelta(days=5))
    create_replacement_request(
        request_id=request_id,
        customer_id=customer_id,
        card_id=card_id,
        reason=reason.lower(),
        replacement_fee="0.00 USD",
        estimated_delivery_date=estimated_delivery_date,
    )
    return {
        "submitted": True,
        "request_id": request_id,
        "card_id": card_id,
        "reason": reason.lower(),
        "estimated_delivery_date": estimated_delivery_date,
    }


@tool
def transfer_to_human(customer_id: str, reason: str) -> dict:
    """Transfer a customer to a trained bank representative for an exception or concern."""
    log_event(customer_id, "human_handoff", {"reason": reason})
    return {"transferred": True, "customer_id": customer_id, "reason": reason}
