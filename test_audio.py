import streamlit as st
from pydub import AudioSegment

st.title("🎤 FFmpeg Test – Audio Conversion")

# Upload audio file
uploaded_file = st.file_uploader("Upload a WAV file to convert into MP3", type=["wav"])

if uploaded_file is not None:
    # Save uploaded file temporarily
    with open("temp.wav", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Convert wav → mp3
    sound = AudioSegment.from_wav("temp.wav")
    sound.export("output.mp3", format="mp3")

    st.success("✅ Conversion done! Saved as output.mp3")
    st.audio("output.mp3")