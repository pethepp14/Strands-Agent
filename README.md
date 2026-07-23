# Card Replacement Assistant

A starter conversational AI agent for a bank that helps customers replace lost,
stolen, damaged, expired, or undelivered debit and credit cards. It is built
with [Strands Agents](https://strandsagents.com/) and uses mock banking tools.

> This repository is a demonstration only. It does not connect to a bank,
> process real card data, or provide production-grade authentication.

See [ARCHITECTURE.md](ARCHITECTURE.md) for the system architecture and
replacement workflow diagrams.

See [OLLAMA_INTEGRATION.md](OLLAMA_INTEGRATION.md) for the local model
connection, architecture, and request lifecycle.

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

Questions outside card replacement are rejected before reaching the model, so
the agent will not attempt banking tool calls for unrelated requests.

It transfers the customer to a human representative when authentication fails,
fraud is suspected, a transaction is disputed, or a request is outside policy.

## Setup

Requires Python 3.10 or later.

```bash
python -m pip install -r requirements.txt
```

## Local model setup

This project uses [Ollama](https://ollama.com/) to run its language model on
your computer. No paid model subscription or API key is required.

Install Ollama, then download the default local model:

```bash
ollama pull llama3.1
```

If Ollama is not already running as a service, start it in a separate terminal:

```bash
ollama serve
```

The project defaults to `llama3.1` at `http://localhost:11434`. To use a model
you have already downloaded, set the model name before starting the app:

```bash
export OLLAMA_MODEL_ID=your-local-model-name
python -m streamlit run app.py
```

## Run the demo

### Terminal chat

```bash
python agent.py
```

### Streamlit web interface

```bash
python -m streamlit run app.py
```

The Streamlit interface keeps chat history and a dedicated agent instance per
browser session. Use **Start new conversation** in its sidebar to clear both.

The repository contains 500 fictional customers in `data/mock_customers.json`.
For the mock flow, use the ten-digit customer ID `1000000001` and a secure
verification-session reference that begins with `verified-`, such as
`verified-1000000001`.
Each synthetic customer has one debit and one credit card.

## Demo database

The tools use the local SQLite database at `data/card_replacement.db`. It is
created and seeded automatically the first time the tools load. Its schema has
four tables: `customers`, `cards`, `replacement_requests`, and `audit_events`.

You can initialize it manually:

```bash
python -m database.seed
```

To reset the synthetic data and remove all demo replacement requests and audit
events, run:

```bash
python -m database.seed --reset
```

The SQLite file is intentionally ignored by Git because it changes whenever a
demo card is blocked or a replacement request is submitted. The JSON generator
remains the reproducible source of the synthetic data.

Example conversation:

```text
Customer: I lost my credit card.
Assistant: I can help protect and replace it. Please complete secure verification.

Customer: My customer ID is 1000000001 and my verification session is verified-1000000001.
Assistant: I found your masked credit card. Would you like me to block it?

Customer: Yes, block it and send a replacement.
Assistant: Your card is blocked. After confirming delivery terms, I can submit the replacement.
```

## Project files

| File | Purpose |
| --- | --- |
| `agent.py` | Agent instructions, tool registration, and interactive entry point. |
| `app.py` | Streamlit-based browser chat interface. |
| `tools/` | Mock banking-tool package; replace its implementations with secured bank-service integrations. |
| `database/` | SQLite schema, data-access functions, and database initialization command. |
| `data/mock_customers.json` | Generated synthetic data for 500 fictional customers and 1,000 cards. |
| `data/generate_mock_data.py` | Deterministic script to regenerate the synthetic dataset. |
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

Replace the SQLite demo layer and tool bodies with your banking services, add
automated tests for each workflow, and deploy the agent behind your existing
customer-authentication and observability layers.
