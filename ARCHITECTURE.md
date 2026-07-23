# Card Replacement Assistant Architecture

This design keeps the language model responsible for conversation and workflow
guidance, while authenticated backend services enforce every sensitive banking
operation.

## System architecture

```mermaid
flowchart LR
    C[Customer] --> UI[Streamlit web UI - demo]
    UI --> GW[API gateway / session layer]
    GW --> AUTH[Bank authentication service]
    GW --> A[Strands card replacement agent]
    A --> MODEL[Ollama local model]

    A --> P[Replacement policy and safety instructions]
    A --> T[Tool layer]
    T --> DB[(SQLite demo database<br/>current MVP)]
    T -. production integration .-> CARD[Card-management service]
    T -. production integration .-> ELIG[Eligibility and fee service]
    T -. production integration .-> DEL[Address and delivery service]
    T -. production integration .-> CASE[Replacement request service]
    T --> ESC[Human-agent handoff]

    AUTH --> AUDIT[Audit and monitoring]
    DB --> AUDIT
    CARD --> AUDIT
    ELIG --> AUDIT
    CASE --> AUDIT
    ESC --> H[Bank representative]
    H --> UI
```

## Replacement workflow

```mermaid
flowchart TD
    START([Customer asks to replace a card]) --> REASON[Identify card type and reason]
    REASON --> SAFE{Sensitive data supplied?}
    SAFE -->|Yes| WARN[Do not process it; direct customer to secure channel]
    WARN --> AUTH
    SAFE -->|No| AUTH[Confirm bank authentication]

    AUTH --> VERIFIED{Verification successful?}
    VERIFIED -->|No| HANDOFF[Transfer to human representative]
    VERIFIED -->|Yes| CARDS[List masked eligible cards]
    CARDS --> SELECT[Customer selects card]
    SELECT --> LOST{Lost or stolen?}

    LOST -->|Yes| BLOCK_CONFIRM[Explain impact and request blocking confirmation]
    BLOCK_CONFIRM --> BLOCKED{Confirmed?}
    BLOCKED -->|No| HANDOFF
    BLOCKED -->|Yes| BLOCK[Block card through card-management service]
    BLOCK --> ELIGIBILITY

    LOST -->|No| ELIGIBILITY[Check eligibility, fee, address, and delivery estimate]
    ELIGIBILITY --> ELIGIBLE{Eligible?}
    ELIGIBLE -->|No| HANDOFF
    ELIGIBLE -->|Yes| DISCLOSE[Disclose replacement terms]
    DISCLOSE --> ORDER_CONFIRM{Customer explicitly confirms?}
    ORDER_CONFIRM -->|No| END([No request submitted])
    ORDER_CONFIRM -->|Yes| SUBMIT[Submit replacement request]
    SUBMIT --> RESULT{Submission successful?}
    RESULT -->|No| HANDOFF
    RESULT -->|Yes| CONFIRM[Return reference number and delivery estimate]
    CONFIRM --> END_SUCCESS([Replacement request complete])
```

## Responsibility boundaries

| Component | Responsibility | Must not do |
| --- | --- | --- |
| Customer channel | Presents chat and established customer session | Send card secrets to the model |
| Strands agent | Converses, gathers non-sensitive context, calls approved tools | Authenticate users or enforce bank policy by prompt alone |
| Tool layer | Validates inputs and invokes backend services | Trust model-provided authorization without server-side checks |
| Bank services | Enforce identity, permissions, policy, card actions, and records | Return full PAN, CVV, PIN, password, or OTP to the agent |
| Human representative | Resolves disputes, fraud, failures, and exceptions | Bypass required bank controls |

## Control requirements

- Authentication and authorization must be checked again by each action tool.
- Blocking and replacement submission require explicit customer confirmation.
- The tool layer must enforce idempotency to prevent duplicate replacement orders.
- All card actions should be logged with a customer/session reference, request ID,
  tool result, and correlation ID.
- Fraud signals, disputed transactions, failed verification, and policy exceptions
  go to a human representative.
