import streamlit as st 
import requests
import json 
import uuid
from assistant_core.voice_input import transcibe_audio, text_to_speech

#backend urls
query_url = "https://127.0.0.1:5000/query"
upload_url = "https://127.0.0.1:5000/upload"

st.set_page_config(
    page_title="Accounting Assistant",
    page_icon=":calculator:",
    layout="wide",
)

#custom CSS (background + sidebar + chat bubbles)
st.markdown("""
<style>
            /* Main Background with custom transparent image */
            .stApp {{
                background: url("file:///C:/Projects_ML/Accounting-Assistant-For-Students/Streamlit%20background.png") repeat;
                background-size: cover;
                background-position: center;
                background-attachment: fixed;
                background-color: #f5f7fa;
            }}
            /* Sidebar customization */
            section[data-testid="stSidebar"] {{
                background-color:  #002147; /* navy */
                color: white;
                padding: 20px;
                border-radius: 10px;
            }}
            section[data-testid="stSidebar"] * {{
                color: white !important;
            }}

            /* Title and Subtitle */
            .title {{
                font-size: 35px;
                font-weight: bold;
                color: #002147; /* navy */
                text-align: center;
                margin-bottom: 0;
                font-family: 'Arial Black', sans-serif;}}
            
            .subtitle {{
                font-size: 18px;
                color: #00796B;
                text-align: center;
                margin-top: 0;
                font-family: 'Arial', sans-serif;}}
            
            /* Chat bubbles */
            .user-bubble {{
                background-color: #00796B;
                color: white;
                padding: 10px;
                border-radius: 15px;
                margin: 5px 0px;
                width: fit-content;}}
            
            .assistant-bubble {{
                background-color: #e0e0e0;
                color: black;
                padding: 10px;
                border-radius: 15px;
                margin: 5px 0px;
                width: fit-content;
            }}

            /* Footer */
            .footer {{
                font-size: 13px;
                color: gray;
                text-align: center;
                margin-top: 20px;
                padding-top: 30px;
                font-family: 'Arial', sans-serif;}}
            </style>

""", unsafe_allow_html=True)



st.markdown('<p class="title">📊 Accounting Assistant</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Your AI-powered tutor for Financial Accounting & IFRS Standards</p>', unsafe_allow_html=True)

#session state 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

#document upload section
st.sidebar.subheader("Upload your Accounting Documents")
uploaded_files = st.sidebar.file_uploader("Upload class notes, textbooks, or past questions (PDF, DOCX, TXT, Images)",
    type=["pdf", "docx", "txt", "png", "jpg", "jpeg"],
    accept_multiple_files=True)

#voice implementation 
voice_input = st.sidebar.checkbox("🎙 Speak my query")
voice_output = st.sidebar.checkbox("🔊 Read answer aloud")



#user inputs - voice or text 
if voice_input:
    st.write("Voice input selected. Please record your question using the button below.")
    audio = st.audio_input("Record your question:")
    if audio:
        #calling the function for speech -> text 
        query = transcibe_audio(audio)
        st.markdown(f'<div class="user-bubble">You: {query}</div>', unsafe_allow_html=True)
    
else:
    query = st.text_input("Enter your question:")
    if query:
        st.markdown(f'<div class="user-bubble">You: {query}</div>', unsafe_allow_html=True)






























st.markdown('<p class = "footer"> Built with ❤️ by Miriam Odeyiany • University of Lagos</p>', unsafe_allow_html=True)