import streamlit as st
from pydub import AudioSegment

def app():
    st.title("🎤 FFmpeg Test – Audio Conversion")
    st.write("✅ Audio Test page loaded!")   # Debug line

    uploaded_file = st.file_uploader(
        "Upload a WAV file to convert into MP3",
        type=["wav"]
    )

    if uploaded_file is not None:
        with open("temp.wav", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Convert WAV -> MP3
        sound = AudioSegment.from_wav("temp.wav")
        sound.export("output.mp3", format="mp3")

        st.success("✅ Conversion done! Saved as output.mp3")

        # Download button
        with open("output.mp3", "rb") as f:
            st.download_button("Download MP3", f, file_name="output.mp3", mime="audio/mpeg")

# Local test ke liye (optional)
if __name__ == "__main__":
    app()