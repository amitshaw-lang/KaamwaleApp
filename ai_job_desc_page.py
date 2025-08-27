# ai_job_desc_page.py
import streamlit as st
from ai_provider import chat

def show_ai_job_desc():
    st.title("📝 AI Job Description Generator")
    title = st.text_input("Job Title", placeholder="e.g., Electrician")
    details = st.text_area("Extra Details (optional)", height=120,
                           placeholder="Shift time, tools, experience, location...")
    lang = st.selectbox("Language", ["English", "Hindi"])

    if st.button("Generate Description"):
        if not title:
            st.warning("Please enter a job title.")
            return

        prompt = (
            f"Write a clear, concise job description for the role '{title}'. "
            f"Audience: Indian blue-collar workers. Keep it simple and friendly. "
            f"Include responsibilities, required skills, location basics, shift, and pay range placeholders. "
            f"Language: {lang}. Extra details (optional): {details}"
        )
        with st.spinner("Generating..."):
            jd = chat(prompt, system="You write short, practical job descriptions for RozgarWale users in India.")
        st.success("Generated JD")
        st.text_area("Preview", jd, height=260)
        st.download_button("⬇️ Download JD (.txt)", jd, file_name=f"{title}_JD.txt")