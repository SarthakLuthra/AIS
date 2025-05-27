import streamlit as st
import requests
import fitz  # PyMuPDF

TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

def ask_together_ai(prompt):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "messages": [
            {"role": "system", "content": "You are a helpful AI study assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- Streamlit UI ---
st.set_page_config(page_title="AI Study Assistant")
st.title("📚 Personal AI Study Assistant")

st.header("📝 PDF Upload + Summarization")
uploaded_pdf = st.file_uploader("Upload your study PDF", type=["pdf"])

if uploaded_pdf:
    with st.spinner("Reading your file..."):
        pdf_text = extract_text_from_pdf(uploaded_pdf)
        if len(pdf_text) > 15000:
            st.warning("PDF is too long! Only summarizing first 15000 characters.")
            pdf_text = pdf_text[:15000]

        prompt = f"Please summarize the following study material:\n\n{pdf_text}"
        summary = ask_together_ai(prompt)
        st.subheader("🧠 Summary")
        st.success(summary)
