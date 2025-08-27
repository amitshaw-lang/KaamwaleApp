# voice_job_posting_page.py
import streamlit as st
import tempfile, os
from pydub import AudioSegment
import speech_recognition as sr

def show_voice_job_posting():
    st.title("🎙️ Voice Job Posting")
    st.caption("RozgarWale – Upload your voice and auto-convert to text")

    uploaded_file = st.file_uploader(
        "📤 Upload voice file (.wav / .mp3)", type=["wav", "mp3"]
    )

    if not uploaded_file:
        st.info("Upload a voice file to start.")
        return

    # 1) Save temp file
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(uploaded_file.read())
        temp_path = tmp.name

    # 2) If MP3 → convert to WAV for recognizer
    input_path = temp_path
    if uploaded_file.type in ("audio/mpeg", "audio/mp3"):
        try:
            sound = AudioSegment.from_file(temp_path, format="mp3")
            wav_path = temp_path + "_converted.wav"
            sound.export(wav_path, format="wav")
            input_path = wav_path
        except Exception as e:
            st.error(f"MP3 convert error: {e}")
            os.remove(temp_path)
            return

    # 3) Play audio
    st.audio(input_path, format="audio/wav")

    # 4) Recognize speech (Hindi by default)
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(input_path) as source:
            audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data, language="hi-IN")
        st.success("📝 Converted Text:")
        st.write(text)

        # 5) WhatsApp share (URL‑encode spaces only; simple)
        whatsapp_link = f"https://wa.me/?text={text.replace(' ', '%20')}"
        st.markdown(f"[💬 Send to WhatsApp]({whatsapp_link})", unsafe_allow_html=True)

    except sr.UnknownValueError:
        st.error("❌ Could not understand the audio.")
    except sr.RequestError:
        st.error("❌ Speech service not reachable.")
    except Exception as e:
        st.error(f"Unexpected error: {e}")
    finally:
        try:
            os.remove(temp_path)
            if input_path != temp_path and os.path.exists(input_path):
                os.remove(input_path)
        except Exception:
            pass