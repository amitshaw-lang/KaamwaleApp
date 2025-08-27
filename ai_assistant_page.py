# ai_assistant_page.py
import streamlit as st
from ai_provider import chat

SYSTEM_PROMPT = (
    "You are RozgarWale's helpful assistant for blue-collar jobs in India. "
    "Reply briefly, Hinglish allowed, avoid unsafe advice."
)

def show_ai_assistant():
    st.title("🤖 RozgarWale AI Assistant")
    st.caption("Ask anything about jobs, pricing, JD, profiles, etc.")

    if "ai_chat" not in st.session_state:
        st.session_state.ai_chat = []

    # history
    for role, msg in st.session_state.ai_chat:
        with st.chat_message(role):
            st.markdown(msg)

    user_msg = st.chat_input("Type your question...")
    if user_msg:
        st.session_state.ai_chat.append(("user", user_msg))
        with st.chat_message("user"):
            st.markdown(user_msg)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                reply = chat(user_msg, system=SYSTEM_PROMPT)
                st.markdown(reply)
        st.session_state.ai_chat.append(("assistant", reply))

    if st.button("🧹 Clear chat"):
        st.session_state.ai_chat = []
        st.experimental_rerun()