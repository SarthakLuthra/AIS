import streamlit as st
import requests
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import io
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
    

import textwrap
from reportlab.lib.pagesizes import A4

def generate_pdf(chat_history):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    textobject = c.beginText(40, height - 40)  # Start near top of page with margin
    textobject.setFont("Helvetica", 12)

    max_width = 100  # Adjust this as needed for page width (characters per line)

    for entry in chat_history:
        if "user" in entry:
            sender = "User"
            message = entry["user"]
        elif "assistant" in entry:
            sender = "Assistant"
            message = entry["assistant"]
        else:
            continue

        # Write sender
        textobject.textLine(f"{sender}:")
        # Wrap message lines and indent them
        wrapped_lines = []
        for line in message.splitlines():
            wrapped = textwrap.wrap(line, width=max_width)
            for wline in wrapped:
                wrapped_lines.append(f"    {wline}")
        for wline in wrapped_lines:
            textobject.textLine(wline)

        textobject.textLine("")  # Add a blank line between messages

        # Check for page overflow
        if textobject.getY() < 40:
            c.drawText(textobject)
            c.showPage()
            textobject = c.beginText(40, height - 40)
            textobject.setFont("Helvetica", 12)

    c.drawText(textobject)
    c.save()
    buffer.seek(0)
    return buffer



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


