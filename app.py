import streamlit as st
from streamlit_mic_recorder import mic_recorder
import speech_recognition as sr
import google.generativeai as genai

# Gemini
genai.configure(api_key="YOUR_GEMINI_API_KEY")
model = genai.GenerativeModel("gemini-2.5-flash")

st.title("🤖 Hindi Voice Assistant")

audio = mic_recorder(
    start_prompt="🎤 Start Recording",
    stop_prompt="⏹️ Stop Recording",
    key="recorder"
)

if audio:
    st.success("Audio recorded!")

    recognizer = sr.Recognizer()

    with open("temp.wav", "wb") as f:
        f.write(audio["bytes"])

    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)

    try:
        text = recognizer.recognize_google(
            audio_data,
            language="hi-IN"
        )

        st.write("### 👤 You")
        st.write(text)

        response = model.generate_content(
            f"Reply in Hindi/Hinglish: {text}"
        )

        answer = response.text

        st.write("### 🤖 AI")
        st.write(answer)

    except Exception as e:
        st.error(str(e))