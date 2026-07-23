"""Simple deterministic scope checks for the card replacement demo."""

from __future__ import annotations


OUT_OF_SCOPE_MESSAGE = (
    "I can help only with debit or credit card replacement requests, such as cards "
    "that are lost, stolen, damaged, expired, or not received. I can’t help with "
    "general questions outside of card replacement."
)

# This is intentionally evaluated before the model is called. It prevents an
# unrelated question from being interpreted as a request to call a banking tool.
CARD_REPLACEMENT_TERMS = (
    "card",
    "credit",
    "debit",
    "replace",
    "replacement",
    "lost",
    "stolen",
    "damage",
    "damaged",
    "expire",
    "expired",
    "not received",
    "delivery",
    "block",
)


def is_card_replacement_query(message: str) -> bool:
    """Return whether an initial message is clearly related to card replacement."""
    normalized_message = message.casefold()
    return any(term in normalized_message for term in CARD_REPLACEMENT_TERMS)
