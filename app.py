import streamlit as st
from audiorecorder import audiorecorder
from groq import Groq
from dotenv import load_dotenv
import speech_recognition as sr
import edge_tts
import asyncio
import tempfile
import os

# =====================================
# CONFIG
# =====================================

load_dotenv()
print("GROQ_API_KEY =", os.getenv("GROQ_API_KEY"))

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# if not GROQ_API_KEY:
#     st.error("GROQ_API_KEY not found in .env file")
#     st.stop()

client = Groq(api_key=GROQ_API_KEY)

# =====================================
# PAGE CONFIG
# =====================================

st.set_page_config(
    page_title="Hindi Voice Assistant",
    page_icon="🤖",
    layout="wide"
)

# =====================================
# CUSTOM CSS
# =====================================

st.markdown("""
<style>
.main {
    padding-top: 1rem;
}
</style>
""", unsafe_allow_html=True)

# =====================================
# TITLE
# =====================================

st.title("🤖 Hindi Voice Assistant")
st.caption("Groq + Hindi + Hinglish + Voice")

# =====================================
# MEMORY
# =====================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# =====================================
# SIDEBAR
# =====================================

with st.sidebar:

    st.header("⚙️ Settings")

    voice_choice = st.selectbox(
        "Voice",
        ["Male", "Female"]
    )

    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()

    st.divider()

    st.subheader("Conversation History")

    for msg in reversed(
        st.session_state.chat_history[-10:]
    ):
        st.write(
            f"**{msg['role']}**: {msg['content']}"
        )

# =====================================
# VOICE CONFIG
# =====================================

voice_name = (
    "hi-IN-MadhurNeural"
    if voice_choice == "Male"
    else "hi-IN-SwaraNeural"
)

# =====================================
# TEXT TO SPEECH
# =====================================

async def generate_voice(text):

    output_file = "response.mp3"

    communicate = edge_tts.Communicate(
        text=text,
        voice=voice_name
    )

    await communicate.save(output_file)

    return output_file

# =====================================
# AI RESPONSE
# =====================================

def ask_ai(user_text):

    history = ""

    for item in st.session_state.chat_history:

        history += (
            f"{item['role']}: "
            f"{item['content']}\n"
        )

    prompt = f"""
आप एक Smart Indian Voice AI Assistant हैं।

Rules:
- Hindi या Hinglish में जवाब दें
- 2-4 वाक्यों में जवाब दें
- बहुत लंबे उत्तर न दें
- Friendly और natural रहें
- User का नाम Ritik है
- Programming questions के लिए examples दें

Conversation History:
{history}

User:
{user_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

# =====================================
# VOICE INPUT
# =====================================

st.subheader("🎤 Voice Input")

audio = audiorecorder(
    "🎙️ Start Recording",
    "⏹️ Stop Recording"
)

if len(audio) > 0:

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_audio:

            audio.export(
                temp_audio.name,
                format="wav"
            )

            audio_path = temp_audio.name

        recognizer = sr.Recognizer()

        with sr.AudioFile(audio_path) as source:

            audio_data = recognizer.record(
                source
            )

        user_text = recognizer.recognize_google(
            audio_data,
            language="hi-IN"
        )

        st.chat_message(
            "user"
        ).write(user_text)

        answer = ask_ai(user_text)

        st.chat_message(
            "assistant"
        ).write(answer)

        st.session_state.chat_history.append(
            {
                "role": "User",
                "content": user_text
            }
        )

        st.session_state.chat_history.append(
            {
                "role": "Assistant",
                "content": answer
            }
        )

        voice_file = asyncio.run(
            generate_voice(answer)
        )

        with open(
            voice_file,
            "rb"
        ) as f:

            audio_bytes = f.read()

        st.audio(
            audio_bytes,
            format="audio/mp3",
            autoplay=True
        )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )

# =====================================
# TEXT CHAT
# =====================================

st.divider()

st.subheader("💬 Text Chat")

text_query = st.chat_input(
    "Ask anything..."
)

if text_query:

    try:

        st.chat_message(
            "user"
        ).write(text_query)

        answer = ask_ai(text_query)

        st.chat_message(
            "assistant"
        ).write(answer)

        st.session_state.chat_history.append(
            {
                "role": "User",
                "content": text_query
            }
        )

        st.session_state.chat_history.append(
            {
                "role": "Assistant",
                "content": answer
            }
        )

        voice_file = asyncio.run(
            generate_voice(answer)
        )

        with open(
            voice_file,
            "rb"
        ) as f:

            audio_bytes = f.read()

        st.audio(
            audio_bytes,
            format="audio/mp3",
            autoplay=True
        )

    except Exception as e:

        st.error(
            f"Error: {str(e)}"
        )