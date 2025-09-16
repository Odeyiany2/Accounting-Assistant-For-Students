import streamlit as st 
import requests
from assistant_core.voice_input import transcibe_audio, text_to_speech
from config.logging import main_app_logger

#backend urls
query_url = "http://127.0.0.1:5000/query"
upload_url = "http://127.0.0.1:5000/upload"

st.set_page_config(
    page_title="Accounting Assistant",
    page_icon=":calculator:",
    layout="wide",
)

#custom CSS (background + sidebar + chat bubbles)

page_bg_img = """
<style>
[data-testid = "stAppViewContainer"]{
    background: linear-gradient(135deg, #ff9a9e 0%, #fad0c4 100%);
    background-size: cover;
    background-attachment: fixed;
}
[data-testid="stAppViewContainer"] .body, p, h1, h4, h2, h3, h5, h6 {
    color: black !important;
    font-family: 'Arial', sans-serif;
}

[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}
[data-testid="stSidebar"] {
    background: #ffe3e3;  /* soft blush pink */
    color: black;
    font-family: 'Arial', sans-serif;
    padding: 15px;
    border-radius: 12px;
}

/*Title and Subtitle */
.title {
    font-size: 36px;
    font-weight: bold;
    color: #D32F2F;  /* deep red */
    text-align: center;
    margin-bottom: 0;
    font-family: 'Arial Black', sans-serif;
}
.subtitle {
    font-size: 18px;
    color: #6d4c41;  /* warm brown */
    text-align: center;
    margin-top: 0;
    font-family: 'Arial', sans-serif;
}

/* Chat bubbles */ 
.user-bubble {
    background: linear-gradient(135deg, #ff758c, #ff7eb3);
    color: white;
    padding: 10px 15px;
    border-radius: 18px;
    margin: 8px 0;
    width: fit-content;
    max-width: 75%;
    font-family: 'Arial', sans-serif;
}
.assistant-bubble {
    background: #fff3f3;
    color: #2e2e2e;
    padding: 10px 15px;
    border-radius: 18px;
    margin: 8px 0;
    width: fit-content;
    max-width: 75%;
    border: 1px solid #ffd1d1;
}
/* Footer */
.footer {
    font-size: 13px;
    color: #6d4c41;
    text-align: center;
    margin-top: 30px;
    padding-top: 20px;
}

</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# ---Page Title and Subtitle ---
st.title("📊 Accounting Assistant")
st.write("*Your AI-powered tutor for Financial Accounting & IFRS Standards*")



#session state 
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

#document upload section
st.sidebar.subheader("✨ Upload your Accounting Documents")
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

# Sidebar options
voice_input = st.sidebar.checkbox("🎙 Speak my query")
voice_output = st.sidebar.checkbox("🔊 Read answer aloud")

# Show chat history in ChatGPT-style UI
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for role, content in st.session_state.chat_history:
    with st.chat_message(role):
        st.markdown(content)

query = None
audio = None

# --- Voice input OR text input ---
if voice_input:
    st.info("🎙 Voice input selected. Record your question below.")
    audio = st.audio_input("Record your question:")
    if audio:
        query = transcibe_audio(audio)
        # Show user voice query in chat
        st.session_state.chat_history.append(("user", query))
        with st.chat_message("user"):
            st.markdown(query)
else:
    query = st.chat_input(
        placeholder="E.g., 'Explain revenue recognition according to IFRS 15'",
        key="prompt"
    )
    if query:
        # Show user text query in chat
        st.session_state.chat_history.append(("user", query))
        with st.chat_message("user"):
            st.markdown(query)

# --- Handle assistant response ---
if query:
    try:
        payload = {
            "query": query,
            "session_id": st.session_state.session_id,
            "history": st.session_state.chat_history,
        }
        response = requests.post(query_url, json=payload, verify=False)

        if response.status_code == 200:
            answer = response.text

            # Add assistant response to chat history
            st.session_state.chat_history.append(("assistant", answer))
            with st.chat_message("assistant"):
                st.markdown(answer)

            if voice_output:
                audio_file = text_to_speech(answer)
                st.audio(audio_file, format="audio/wav")

        else:
            st.error("⚠️ Failed to get response from assistant. Try again!")
            main_app_logger.error(f"Failed to get response from assistant. Status code: {response.status_code}, Response: {response.text}")

    except Exception as e:
        st.error("❌ An error occurred while querying the assistant.")
        main_app_logger.error(f"Exception during querying assistant: {e}")









# st.write("---")

# st.markdown("Built with ❤️ by Miriam Odeyiany • University of Lagos © 2025")
# st.markdown("Find the project on [GitHub](https://github.com/Odeyiany2/Accounting-Assistant-For-Students)")