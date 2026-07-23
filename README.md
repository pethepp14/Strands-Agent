# Card Replacement Assistant

A starter conversational AI agent for a bank that helps customers replace lost,
stolen, damaged, expired, or undelivered debit and credit cards. It is built
with [Strands Agents](https://strandsagents.com/) and uses mock banking tools.

> This repository is a demonstration only. It does not connect to a bank,
> process real card data, or provide production-grade authentication.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the system architecture and
replacement workflow diagrams.

## What it does

The agent follows a controlled replacement workflow:

1. Identifies the customer's replacement reason and card type.
2. Requires secure authentication before showing card details or acting.
3. Lists cards using masked details only.
4. For a lost or stolen card, obtains confirmation and blocks it first.
5. Checks replacement eligibility and discloses fee, delivery address, and
   delivery estimate.
6. Obtains explicit confirmation before submitting the replacement.
7. Returns a replacement request reference and expected delivery date.

It transfers the customer to a human representative when authentication fails,
fraud is suspected, a transaction is disputed, or a request is outside policy.

## Setup

Requires Python 3.10 or later.

```bash
pip install -r requirements.txt
```

Configure the model credentials required by your Strands provider before
starting the agent. Refer to your Strands model-provider setup for the relevant
environment variables and authentication method.

## Run the demo

```bash
python agent.py
```

For the mock flow, the available customer ID is `customer-demo`. The demo
authentication tool accepts a secure verification-session reference that starts
with `verified-`, such as `verified-demo-session`.

Example conversation:

```text
Customer: I lost my credit card.
Assistant: I can help protect and replace it. Please complete secure verification.

Customer: My customer ID is customer-demo and my verification session is verified-demo-session.
Assistant: I found your masked credit card. Would you like me to block it?

Customer: Yes, block it and send a replacement.
Assistant: Your card is blocked. After confirming delivery terms, I can submit the replacement.
```

## Project files

| File | Purpose |
| --- | --- |
| `agent.py` | Agent instructions, mock data, mock bank tools, and interactive entry point. |
| `requirements.txt` | Python dependencies. |
| `__init__.py` | Package initializer. |

## Available tools

The tools in `agent.py` are mocks that demonstrate the backend contract an
actual bank integration would need:

- `authenticate_customer` confirms a completed secure-authentication session.
- `list_customer_cards` returns eligible cards using only masked details.
- `block_card` blocks a confirmed lost or stolen card.
- `check_replacement_eligibility` returns eligibility, fee, destination, and delivery terms.
- `submit_replacement_request` submits a confirmed replacement request.
- `transfer_to_human` hands an exception to a representative.

## Security and production requirements

Before using this design in production, replace every mock tool with a secured,
audited banking API integration. In particular:

- Use the bank's existing authenticated session; do not have the model collect
  credentials or one-time passcodes.
- Never expose or store full card numbers, CVVs, PINs, passwords, or OTPs.
- Enforce authorization, confirmation, idempotency, rate limits, audit logging,
  and fraud controls in the backend tools—not only in the agent prompt.
- Use PCI DSS-compliant systems and follow the applicable banking, privacy, and
  consumer-protection requirements for your jurisdiction.
- Keep human escalation available for fraud, disputes, policy exceptions, and
  failed verification.

## Next steps

Replace the mock `CARDS` data and tool bodies with your banking services, add
automated tests for each workflow, and deploy the agent behind your existing
customer-authentication and observability layers.
