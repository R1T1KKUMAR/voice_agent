import speech_recognition as sr
import google.generativeai as genai
import asyncio
import edge_tts
import pygame
import os

# =====================================
# GEMINI API KEY
# =====================================
GEMINI_API_KEY = "YOUR_API"

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")

# =====================================
# SPEAK FUNCTION (Hindi Voice)
# =====================================
async def speak(text):

    print(f"\n🤖 AI: {text}\n")

    filename = "response.mp3"

    communicate = edge_tts.Communicate(
        text=text,
        voice="hi-IN-MadhurNeural"
    )

    await communicate.save(filename)

    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        await asyncio.sleep(0.1)

    pygame.mixer.music.unload()

    if os.path.exists(filename):
        os.remove(filename)


# =====================================
# MICROPHONE SETUP
# =====================================
recognizer = sr.Recognizer()

def listen():

    try:
        with sr.Microphone() as source:

            print("\n🎤 बोलिए...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            audio = recognizer.listen(
                source,
                timeout=15,
                phrase_time_limit=20
            )

            print("🔍 समझ रहा हूँ...")

            text = recognizer.recognize_google(
                audio,
                language="hi-IN"
            )

            print(f"\n👤 You: {text}")

            return text

    except sr.WaitTimeoutError:
        print("⌛ कोई आवाज़ नहीं मिली")
        return None

    except sr.UnknownValueError:
        print("😔 मैं समझ नहीं पाया")
        return None

    except Exception as e:
        print("Error:", e)
        return None


# =====================================
# MEMORY
# =====================================
chat_history = []

def ask_gemini(user_text):

    try:

        history_text = ""

        for msg in chat_history:
            history_text += f"{msg['role']}: {msg['content']}\n"

        prompt = f"""
आप एक दोस्ताना भारतीय AI Assistant हैं।

नियम:
1. हमेशा हिंदी या Hinglish में उत्तर दें।
2. उत्तर छोटे और स्पष्ट रखें।
3. यदि यूज़र अंग्रेज़ी में पूछे तो भी आसान हिंदी/Hinglish में समझाएँ।
4. बातचीत का संदर्भ याद रखें।

Conversation:
{history_text}

User: {user_text}
"""

        response = model.generate_content(prompt)

        answer = response.text

        chat_history.append(
            {
                "role": "User",
                "content": user_text
            }
        )

        chat_history.append(
            {
                "role": "Assistant",
                "content": answer
            }
        )

        return answer

    except Exception as e:
        return f"Gemini Error: {e}"


# =====================================
# START
# =====================================
print("=" * 50)
print("🚀 Hindi Gemini Voice Assistant Started")
print("=" * 50)

asyncio.run(
    speak(
        "नमस्ते रितिक कुमार। मैं आपका हिंदी एआई असिस्टेंट हूँ।"
    )
)

# =====================================
# MAIN LOOP
# =====================================
while True:

    user_text = listen()

    if not user_text:
        continue

    if user_text.lower() in [
        "बंद करो",
        "रुको",
        "अलविदा",
        "बाय",
        "exit",
        "quit",
        "stop"
    ]:

        asyncio.run(
            speak(
                "अलविदा रितिक कुमार। आपका दिन शुभ हो।"
            )
        )

        break

    answer = ask_gemini(user_text)

    asyncio.run(
        speak(answer)
    )
