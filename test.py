import streamlit as st 
import requests
from assistant_core.voice_input import transcibe_audio, text_to_speech
from config.logging import main_app_logger

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



st.markdown(
    '<p style="font-size:35px; font-weight:bold; color:#002147; text-align:center;">📊 Accounting Assistant</p>',
    unsafe_allow_html=True
)

st.markdown(
    '<p style="font-size:18px; color:#00796B; text-align:center;">Your AI-powered tutor for Financial Accounting & IFRS Standards</p>',
    unsafe_allow_html=True
)

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

if uploaded_files and st.sidebar.button("Upload"):
    try:
        files = [("files", (file.name, file, file.type)) for file in uploaded_files]
        response = requests.post(upload_url, files = files)

        if response.status_code == 200:
            result = response.json()
            st.session_state.session_id = result.get("session_id")
            main_app_logger.info(f"Files uploaded successfully. Session ID: {st.session_state.session_id}")
            st.sidebar.success(f"Successfully uploaded {len(uploaded_files)} file(s).")
        else:
            main_app_logger.error(f"Failed to upload files. Status code: {response.status_code}, Response: {response.text}")
            st.sidebar.error("Failed to upload files. Please try again.")
    except Exception as e:
        main_app_logger.error(f"Exception during file upload: {e}")
        st.sidebar.error("An error occurred during file upload. Please try again.")



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



#handling the query and getting the response from the backend
if (voice_input and audio) or (not voice_input and query):
    try:
        payload = {
            "query": query,
            "session_id": st.session_state.session_id,
            "history": st.session_state.chat_history
        }
        response = requests.post(query_url, json=payload, verify=False)

        if response.status_code == 200:
            answer = response.text

            #update chat history
            st.session_state.chat_history.append(("User", query))
            st.session_state.chat_history.append(("Assistant", answer))

            #display assistant bubble
            st.markdown(f'<div class="assistant-bubble">Assistant: {answer}</div>', unsafe_allow_html=True)
            main_app_logger.info(f"Received answer from assistant: {answer}")

            if voice_output:
                audio_file = text_to_speech(answer)
                st.audio(audio_file, format="audio/wav")
        else:
            main_app_logger.error(f"Failed to get response from assistant. Status code: {response.status_code}, Response: {response.text}")
            st.error("Failed to get response from assistant. Please try again.")
    except Exception as e:
        main_app_logger.error(f"Exception during querying assistant: {e}")
        st.error("An error occurred while querying the assistant. Please try again.")










st.markdown('<p class = "footer"> Built with ❤️ by Miriam Odeyiany • University of Lagos</p>', unsafe_allow_html=True)