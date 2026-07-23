"""A safe starter for a debit and credit card replacement assistant.

This module uses mock data only. Replace the tool bodies with authenticated,
audited calls to the bank's card-management services before production use.
"""

from __future__ import annotations

import os

from strands import Agent
from strands.models.ollama import OllamaModel

if __package__:
    from .tools import (
        authenticate_customer,
        block_card,
        check_replacement_eligibility,
        list_customer_cards,
        submit_replacement_request,
        transfer_to_human,
    )
else:
    from tools import (
        authenticate_customer,
        block_card,
        check_replacement_eligibility,
        list_customer_cards,
        submit_replacement_request,
        transfer_to_human,
    )


SYSTEM_PROMPT = """
You are a bank assistant for debit- and credit-card replacements.

Scope: You handle only debit- and credit-card replacement requests. If a
customer asks an unrelated question (for example, geography, general knowledge,
or another banking service), politely state that you can help only with card
replacement requests. Do not call a tool for an unrelated question. Never
invent a customer ID, card ID, verification-session reference, or tool input.
For this local demo, customer IDs are ten-digit numeric values, such as
`1000000001`. Ask for the customer's customer ID only after they state that
they completed secure verification; never make up an ID on their behalf.

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
"""


def create_local_model() -> OllamaModel:
    """Create the locally hosted Ollama model used by the demo."""
    return OllamaModel(
        host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
        model_id=os.getenv("OLLAMA_MODEL_ID", "llama3.1"),
        temperature=0.2,
    )


def create_card_replacement_agent() -> Agent:
    """Create an agent instance for one customer conversation."""
    return Agent(
        name="Card Replacement Assistant",
        model=create_local_model(),
        system_prompt=SYSTEM_PROMPT,
        tools=[
            authenticate_customer,
            list_customer_cards,
            block_card,
            check_replacement_eligibility,
            submit_replacement_request,
            transfer_to_human,
        ],
    )


card_replacement_agent = create_card_replacement_agent()


if __name__ == "__main__":
    print("Card Replacement Assistant (type 'quit' to exit)")
    while True:
        message = input("Customer: ").strip()
        if message.lower() in {"quit", "exit"}:
            break
        print(f"Assistant: {card_replacement_agent(message)}")
