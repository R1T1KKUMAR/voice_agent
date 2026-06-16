import speech_recognition as sr

r = sr.Recognizer()

print("Available microphones:")
print(sr.Microphone.list_microphone_names())

with sr.Microphone() as source:
    print("Speak now...")
    audio = r.listen(source)

print("Recognizing...")
print(r.recognize_google(audio))