# ai_provider.py
import os

def _get_api_key():
    # Streamlit secrets prefer, else environment
    try:
        import streamlit as st
        return st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    except Exception:
        return os.getenv("OPENAI_API_KEY")

def chat(prompt: str, system: str = None, temperature: float = 0.7, max_tokens: int = 800) -> str:
    """
    OpenAI 0.28.1 (legacy) simple chat wrapper.
    """
    import openai
    api_key = _get_api_key()
    if not api_key:
        return "❗ OPENAI_API_KEY missing. Set it in env or .streamlit/secrets.toml"
    openai.api_key = api_key

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return resp["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"⚠️ AI error: {e}"