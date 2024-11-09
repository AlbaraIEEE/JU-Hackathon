import cohere
import streamlit as st
import pyttsx3
from PIL import Image
import pandas as pd
import docx2txt

cohere_client = cohere.Client('8D1jtq9XIVLtaxk9OQSG84jsmmsG7WBMVi9AaKAk')

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def read_image(file):
    image = Image.open(file)
    return image

def read_excel(file):
    df = pd.read_excel(file)
    return df

def read_word(file):

    text = docx2txt.process(file)
    return text

def ask_ques(question):
    prompt = "You are an intelligent, knowledgeable assistant who answers based on the conversation history."
    for turn in st.session_state.chat_history[-5:]:
        prompt += f"\n{turn['role'].capitalize()}: {turn['content']}"
    try:
        response = cohere_client.generate(
            model='command-xlarge-nightly',
            prompt=prompt,
            max_tokens=200,
            temperature=0.2
        )
        answer = response.generations[0].text.strip()
        return answer
    except Exception as e:
        return f"An error occurred: {e}"


if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'old_chats' not in st.session_state:
    st.session_state.old_chats = []
if 'last_question' not in st.session_state:
    st.session_state.last_question = None


st.sidebar.title("AI Tutor Settings")
sidebar_option = st.sidebar.selectbox(
    "Choose an option",
    ("Chat Settings", "Help", "About", "Old Chats")
)

if sidebar_option == "Chat Settings":
    st.sidebar.write("You can customize the chat experience here.")
elif sidebar_option == "Help":
    st.sidebar.write("How to interact with the AI:")
    st.sidebar.write("- Type your question in the input box.")
    st.sidebar.write("- The AI will answer based on prior conversation.")
elif sidebar_option == "About":
    st.sidebar.write("This is an AI-powered tutor built with Cohere API.")
elif sidebar_option == "Old Chats":
    st.sidebar.write("Select a previous chat to view:")
    for i, chat in enumerate(st.session_state.old_chats):
        if st.sidebar.button(f"Chat {i+1}", key=f"chat_{i}"):
            st.session_state.chat_history = chat

st.markdown("""
    <style>
        .stApp { background-color: #fafafa; font-family: Arial, sans-serif; }
        .chat-container { height: 400px; overflow-y: scroll; padding: 10px; margin-bottom: 70px; }
        .user-message { background-color: #DCF8C6; color: #000; padding: 10px; border-radius: 12px; margin-bottom: 10px; text-align: right; align-self: flex-end; width: fit-content; max-width: 75%; }
        .assistant-message { background-color: #f1f0f0; color: #333; padding: 10px; border-radius: 12px; margin-bottom: 10px; text-align: left; align-self: flex-start; width: fit-content; max-width: 75%; }
        .stTextInput>div>div>input { border-radius: 8px; padding: 10px; border: 1px solid #ddd; font-size: 16px; }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title-container' style='text-align: center; padding: 10px; color: #444;'>AI-Powered Intelligent Tutor</div>", unsafe_allow_html=True)
st.write("Ask any question, and I’ll provide an answer.")
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

for turn in st.session_state.chat_history:
    if turn['role'] == 'user':
        st.markdown(f"<div class='user-message'>{turn['content']}</div>", unsafe_allow_html=True)
    elif turn['role'] == 'assistant':
        st.markdown(f"<div class='assistant-message'>{turn['content']}</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)


uploaded_file = st.file_uploader("Upload a file")
if uploaded_file:
    file_type = uploaded_file.type
    if file_type.startswith("image/"):
        image = read_image(uploaded_file)
        st.image(image, caption="Uploaded Image")
    elif file_type == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        excel_data = read_excel(uploaded_file)
        st.write(excel_data)
    elif file_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        word_text = read_word(uploaded_file)
        st.write(word_text)


question = st.text_input("Your question:", key="user_input")


if st.button("Submit"):
    if question and question != st.session_state.last_question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        answer = ask_ques(question)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        st.session_state.old_chats.append(list(st.session_state.chat_history))
        st.session_state.last_question = question  # Update last question
        st.rerun()  # Ensure the interface updates without duplicating responses
