"""Generate deterministic, non-PII customer and card data for local demos."""

from __future__ import annotations

import json
from pathlib import Path


CUSTOMER_COUNT = 500
NETWORKS = ("Visa", "Mastercard", "RuPay")
OUTPUT_FILE = Path(__file__).with_name("mock_customers.json")


def build_customer(index: int) -> dict:
    """Create one fictional customer with one debit and one credit card."""
    customer_number = f"{index:04d}"
    customer_id = f"{1_000_000_000 + index:010d}"
    return {
        "customer_id": customer_id,
        "display_name": f"Demo Customer {customer_number}",
        "registered_address": (
            f"{index} Demo Lane, Test District, Example City, 100{index % 100:02d}"
        ),
        "cards": [
            {
                "card_id": f"card-credit-{customer_number}",
                "type": "credit",
                "network": NETWORKS[index % len(NETWORKS)],
                "last_four": f"{1000 + index:04d}",
                "status": "active",
            },
            {
                "card_id": f"card-debit-{customer_number}",
                "type": "debit",
                "network": NETWORKS[(index + 1) % len(NETWORKS)],
                "last_four": f"{6000 + index:04d}",
                "status": "active",
            },
        ],
    }


def main() -> None:
    dataset = {
        "metadata": {
            "customer_count": CUSTOMER_COUNT,
            "data_classification": "synthetic demo data - not real customer information",
        },
        "customers": [build_customer(index) for index in range(1, CUSTOMER_COUNT + 1)],
    }
    OUTPUT_FILE.write_text(json.dumps(dataset, indent=2) + "\n", encoding="utf-8")
    print(f"Generated {CUSTOMER_COUNT} synthetic customers in {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
