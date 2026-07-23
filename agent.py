"""A safe starter for a debit and credit card replacement assistant.

This module uses mock data only. Replace the tool bodies with authenticated,
audited calls to the bank's card-management services before production use.
"""

from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from strands import Agent, tool


# Mock data deliberately contains card aliases only--never PAN, CVV, PIN, OTP,
# passwords, or other card-secret values.
CARDS = {
    "customer-demo": [
        {
            "card_id": "card-credit-4821",
            "type": "credit",
            "network": "Visa",
            "last_four": "4821",
            "status": "active",
        },
        {
            "card_id": "card-debit-0914",
            "type": "debit",
            "network": "Mastercard",
            "last_four": "0914",
            "status": "active",
        },
    ]
}

AUTHENTICATED_CUSTOMERS: set[str] = set()


@tool
def authenticate_customer(customer_id: str, verification_session_id: str) -> dict:
    """Confirm authentication completed through the bank's secure verification service.

    Args:
        customer_id: The bank's internal customer identifier.
        verification_session_id: A reference from a completed secure verification flow.
            Never request or accept an OTP, password, PIN, CVV, or full card number.
    """
    if customer_id != "customer-demo" or not verification_session_id.startswith("verified-"):
        return {"authenticated": False, "message": "Secure verification could not be confirmed."}

    AUTHENTICATED_CUSTOMERS.add(customer_id)
    return {"authenticated": True, "customer_id": customer_id}


@tool
def list_customer_cards(customer_id: str) -> dict:
    """List the authenticated customer's eligible cards using masked card details only."""
    if customer_id not in AUTHENTICATED_CUSTOMERS:
        return {"error": "Authentication is required before viewing cards."}
    return {"cards": CARDS.get(customer_id, [])}


@tool
def block_card(customer_id: str, card_id: str, reason: str) -> dict:
    """Immediately block an authenticated customer's lost or stolen card.

    Use only after the customer explicitly confirms blocking the selected card.
    """
    if customer_id not in AUTHENTICATED_CUSTOMERS:
        return {"error": "Authentication is required before blocking a card."}
    if reason.lower() not in {"lost", "stolen"}:
        return {"error": "Blocking through this flow is limited to lost or stolen cards."}

    for card in CARDS.get(customer_id, []):
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
    if not any(card["card_id"] == card_id for card in CARDS.get(customer_id, [])):
        return {"eligible": False, "message": "Card was not found for this customer."}

    return {
        "eligible": True,
        "replacement_fee": "0.00 USD",
        "delivery_estimate": "3-5 business days",
        "address": "registered mailing address",
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


card_replacement_agent = Agent(
    name="Card Replacement Assistant",
    system_prompt="""
You are a bank assistant for debit- and credit-card replacements.

Follow this sequence:
1. Identify the replacement reason and whether the card is debit or credit.
2. Require secure authentication before accessing card details or taking action.
3. Use only masked card details returned by tools to identify a card.
4. For lost or stolen cards, explain that blocking prevents further use, then get
   explicit confirmation and call block_card before placing a replacement request.
5. Check eligibility and clearly state any fee, destination, and delivery estimate.
6. Get explicit confirmation after disclosing those terms, then submit the request.
7. Provide the request reference and delivery estimate.

Never ask for or accept a full card number, CVV, PIN, password, security answer,
or one-time passcode. Never claim that a card is blocked or a replacement is
submitted unless the matching tool reports success. Transfer to a human if fraud
is suspected, a transaction is disputed, authentication fails, or policy is unclear.
""",
    tools=[
        authenticate_customer,
        list_customer_cards,
        block_card,
        check_replacement_eligibility,
        submit_replacement_request,
        transfer_to_human,
    ],
)


if __name__ == "__main__":
    print("Card Replacement Assistant (type 'quit' to exit)")
    while True:
        message = input("Customer: ").strip()
        if message.lower() in {"quit", "exit"}:
            break
        print(f"Assistant: {card_replacement_agent(message)}")
