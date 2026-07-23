"""Streamlit user interface for the card replacement assistant demo."""

from __future__ import annotations

import streamlit as st

from agent import create_card_replacement_agent


st.set_page_config(page_title="Card Replacement Assistant", page_icon="💳")


def start_conversation() -> None:
    """Start a new, session-scoped agent and reset the visible chat history."""
    st.session_state.agent = create_card_replacement_agent()
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Hello. I can help replace a debit or credit card that is lost, "
                "stolen, damaged, expired, or not received. Please do not share "
                "your full card number, CVV, PIN, password, or one-time passcode."
            ),
        }
    ]


if "agent" not in st.session_state or "messages" not in st.session_state:
    start_conversation()

st.title("💳 Card Replacement Assistant")
st.caption("Demo application — mock data and tools only. Do not enter real banking information.")

with st.sidebar:
    st.subheader("Demo controls")
    st.info(
        "Use `customer-0001` and a verification session beginning with `verified-` "
        "for the mock flow. The dataset contains 500 fictional customers."
    )
    if st.button("Start new conversation", use_container_width=True):
        start_conversation()
        st.rerun()

    st.divider()
    st.subheader("Security reminders")
    st.markdown(
        "- Never enter a full card number, CVV, PIN, password, or OTP.\n"
        "- Lost or stolen cards require confirmation before they are blocked.\n"
        "- Replacement requests require confirmation after delivery terms are shown."
    )

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Describe the card replacement you need"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Checking your request..."):
            try:
                response = str(st.session_state.agent(prompt))
            except Exception:
                response = (
                    "I couldn't complete that request in this demo. Please try again "
                    "or contact a bank representative."
                )
        st.markdown(response)

    st.session_state.messages.append({"role": "assistant", "content": response})
