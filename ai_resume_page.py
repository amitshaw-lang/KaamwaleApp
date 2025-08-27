# ai_resume_page.py
import streamlit as st
from ai_provider import chat

def show_ai_resume():
    st.title("📄 AI Resume Generator")
    name = st.text_input("Worker Name", placeholder="e.g., Rakesh Kumar")
    skills = st.text_area("Skills", placeholder="Electrician, Wiring, AC Repair")
    exp = st.text_area("Experience Summary", placeholder="3 years residential wiring, handled 50+ jobs")
    city = st.text_input("City", placeholder="Patna")
    lang = st.selectbox("Language", ["English", "Hindi"])

    if st.button("Generate Resume"):
        if not name or not skills:
            st.warning("Name and Skills are required.")
            return
        prompt = (
            f"Create a one-page resume for a blue-collar worker.\n"
            f"Name: {name}\nCity: {city}\nSkills: {skills}\nExperience: {exp}\n"
            f"Keep it ATS-friendly with bullet points and a short summary. Language: {lang}."
        )
        with st.spinner("Generating..."):
            resume = chat(prompt, system="You create short, ATS-friendly resumes for Indian blue-collar workers.")
        st.text_area("Resume", resume, height=320)
        st.download_button("⬇️ Download Resume (.txt)", resume, file_name=f"{name.replace(' ','_')}_Resume.txt")