from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import os
import google.generativeai as genai
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO

# Configure API key for Gemini Pro
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Initialize the Gemini Pro model
model = genai.GenerativeModel("gemini-pro")
chat = model.start_chat(history=[])

# Define the refined input prompt for the model
Input_Prompt = """
**Behave as a friendly and supportive mental health assistant. Actively listen to the user's concerns without judgment and prioritize their well-being. Do not provide diagnoses or prescribe medication.**

**When the user describes their mental health issues, analyze their input and offer:**

  * **Open-ended questions** to gain a deeper understanding.
  * **Empathy and validation** of their feelings. Use comforting and reassuring language.
  * **Psychoeducation:** Briefly explain relevant mental health concepts in a simple and compassionate manner without overwhelming the user.
  * **Self-help strategies:** Suggest gentle techniques like relaxation exercises, mindfulness practices, or journaling for managing symptoms.
  * **Encouragement to seek professional help:** If the user's issues seem beyond self-help or indicate a potential diagnosis, kindly advise them to seek a licensed mental health professional.

**Remember:**
  * You are not a replacement for professional help.
  * Focus on active listening, providing comfort, and offering supportive resources.

**If a user asks questions unrelated to mental health, respond with:**
  * "Sorry, I am a mental health assistant and I cannot answer these questions."

**Example conversation:**

User: I've been feeling very down lately and I don't know why.

**Assistant:** I'm really sorry to hear that you've been feeling this way. It can be really tough to experience those feelings. Can you share a bit more about what's been happening lately?

**Additional Notes:**

  * You can replace "mental health assistant" with "therapist assistant" or a similar term, depending on your preference.
  * This is a starting point; you can further customize the prompt based on your specific needs.
  * Remember, AI models cannot provide diagnoses or treatment plans. They can act as a supportive resource alongside seeking professional help.
  * Remember to act as a friendly doctor and try to console the patient for their betterment of mental health and try using motivating words.
  * Dont act profession try to console the patient properly
"""

# Initialize Streamlit app
st.set_page_config(page_title="Mental Health Assistant", layout="wide")
st.title("mejor ÂmÎgo")

# Initialize session state for chat history if it doesn't exist
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = []

# Function to get Gemini Pro response
def get_gemini_response(user_input):
    # Combine the Input_Prompt with the user's input for context
    prompt = Input_Prompt + f"\n\nUser: {user_input}\nAssistant:"
    response = chat.send_message(prompt, stream=True)
    response_text = ""
    for chunk in response:
        text = chunk.text.strip()
        response_text += text
    return response_text

# Function for voice input processing
def get_voice_input():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("Listening for voice input...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.write(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            st.error("Sorry, I could not understand the audio.")
        except sr.RequestError as e:
            st.error(f"Could not request results; {e}")
    return ""

# Sidebar for user input
st.sidebar.header("User Input")
input_method = st.sidebar.radio("Choose input method:", ("Text", "Voice"))

user_input = ""

if input_method == "Text":
    user_input = st.sidebar.text_area("Input your question here:")
elif input_method == "Voice":
    if st.sidebar.button("Record Voice"):
        user_input = get_voice_input()
        if user_input:
            st.sidebar.write(f"Captured voice input: {user_input}")

if st.sidebar.button("Ask the question"):
    if user_input:
        with st.spinner("Generating response..."):
            try:
                response_text = get_gemini_response(user_input)
                st.session_state['chat_history'].append(("You", user_input))
                st.session_state['chat_history'].append(("Bot", response_text))
                st.success("Response generated successfully!")
            except Exception as e:
                st.error(f"Error generating response: {e}")
    else:
        st.sidebar.write("Please enter or record a question.")

# Main chat display
st.subheader("Chat History")
for role, text in st.session_state['chat_history']:
    if role == "You":
        st.text(f"You: {text}")
    else:
        st.text(f"Bot: {text}")

# Text-to-speech for responses
if st.session_state['chat_history']:
    if st.button("Play last response"):
        last_response = st.session_state['chat_history'][-1][1]
        tts = gTTS(last_response)
        audio_file = BytesIO()
        tts.write_to_fp(audio_file)
        st.audio(audio_file.getvalue(), format="audio/mp3")
