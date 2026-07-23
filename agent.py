"""A safe starter for a debit and credit card replacement assistant.

This module uses mock data only. Replace the tool bodies with authenticated,
audited calls to the bank's card-management services before production use.
"""

from __future__ import annotations

from strands import Agent

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


def create_card_replacement_agent() -> Agent:
    """Create an agent instance for one customer conversation."""
    return Agent(
        name="Card Replacement Assistant",
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
