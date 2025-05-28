import streamlit as st
import requests
from fpdf import FPDF
from io import BytesIO

# --- PAGE CONFIG ---
st.set_page_config(page_title="📚 AI Study Assistant", layout="centered")
st.title("📚 Personal AI Study Assistant")

# --- SETUP ---
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

# Init chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to ask Together AI
def ask_together_ai(prompt):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "messages": [{"role": "system", "content": "You are a helpful AI study assistant."}] +
                   [{"role": "user", "content": m["user"]} if "user" in m else {"role": "assistant", "content": m["assistant"]}
                    for m in st.session_state.chat_history] +
                   [{"role": "user", "content": prompt}],
        "temperature": 0.7
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Show full chat history
for msg in st.session_state.chat_history:
    if "user" in msg:
        with st.chat_message("user"):
            st.markdown(msg["user"])
    if "assistant" in msg:
        with st.chat_message("assistant"):
            st.markdown(msg["assistant"])

# --- Chat Input ---
user_prompt = st.chat_input("Ask me anything about your study material...")

if user_prompt:
    # Show user message
    with st.chat_message("user"):
        st.markdown(user_prompt)
    st.session_state.chat_history.append({"user": user_prompt})

    # Generate AI response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ask_together_ai(user_prompt)
            st.markdown(response)
    st.session_state.chat_history.append({"assistant": response})
    from fpdf import FPDF
from io import BytesIO

from fpdf import FPDF
from io import BytesIO

def generate_pdf(chat_history):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    pdf.set_title("AI Study Assistant Chat History")
    pdf.set_author("Sarthak's Study Assistant")

    for msg in chat_history:
        if "user" in msg:
            pdf.set_text_color(0, 0, 255)
            pdf.multi_cell(0, 10, f"User: {msg['user']}")
        if "assistant" in msg:
            pdf.set_text_color(0, 100, 0)
            pdf.multi_cell(0, 10, f"AI: {msg['assistant']}")
        pdf.ln(5)

    # Correct way to save to buffer for Streamlit download
    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer, dest='F')
    pdf_buffer.seek(0)
    return pdf_buffer

# Download button
if st.session_state.chat_history:
    st.markdown("---")
    if st.button("📥 Download Chat as PDF"):
        pdf_bytes = generate_pdf(st.session_state.chat_history)
        st.download_button(
            label="Click here to download",
            data=pdf_bytes,
            file_name="chat_history.pdf",
            mime="application/pdf"
        )


