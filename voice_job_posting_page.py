import streamlit as st


def show_voice_job_post_page():
    """APK build placeholder - desktop-only feature."""
    st.info("Voice features are disabled in APK mode.")


# Backwards compatible alias (old import name)
def show_voice_job_posting():
    show_voice_job_post_page()
