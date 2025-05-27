import streamlit as st
import requests
import fitz  # PyMuPDF

st.set_page_config(page_title="AI Study Assistant", layout="centered")

# Get API key from Streamlit secrets
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

# Initialize session state for history
if "history" not in st.session_state:
    st.session_state.history = []

# Function to ask Together AI
def ask_together_ai(prompt):
    url = "https://api.together.xyz/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "messages": [
            {"role": "system", "content": "You are a helpful AI study assistant. Help with summaries, explanations, quizzes, etc."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Function to extract text from PDF
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# --- UI Starts Here ---
st.title("📚 Personal AI Study Assistant")

# Sidebar: History
st.sidebar.title("📜 Interaction History")
if st.session_state.history:
    for idx, entry in enumerate(reversed(st.session_state.history), 1):
        st.sidebar.markdown(f"**{idx}. {entry['type']}**")
        st.sidebar.markdown(f"- 🔹 Input: `{entry['input'][:50]}...`")
        st.sidebar.markdown(f"- 🧠 Output: `{entry['output'][:60]}...`")
        st.sidebar.markdown("---")
else:
    st.sidebar.info("No history yet.")

# Main Selection
st.markdown("Choose an action:")
option = st.radio("Select input type:", ("Ask a question", "Upload a PDF"))

# --- Ask a Question ---
if option == "Ask a question":
    user_query = st.text_input("❓ Enter your question:")
    if st.button("Ask"):
        if user_query.strip():
            with st.spinner("Thinking..."):
                response = ask_together_ai(user_query)
                st.subheader("🧠 AI Response")
                st.success(response)

                st.session_state.history.append({
                    "type": "Question",
                    "input": user_query,
                    "output": response
                })
        else:
            st.warning("Please enter a question.")

# --- Upload a PDF ---
elif option == "Upload a PDF":
    uploaded_pdf = st.file_uploader("📄 Upload a PDF", type=["pdf"])
    if uploaded_pdf:
        if st.button("Summarize PDF"):
            with st.spinner("Reading PDF..."):
                pdf_text = extract_text_from_pdf(uploaded_pdf)
                if len(pdf_text) > 15000:
                    pdf_text = pdf_text[:15000]
                    st.warning("PDF is too long, summarizing first 15000 characters.")

                summary_prompt = f"Summarize this study material:\n\n{pdf_text}"
                summary = ask_together_ai(summary_prompt)
                st.subheader("🧠 Summary")
                st.success(summary)

                st.session_state.history.append({
                    "type": "PDF Summary",
                    "input": uploaded_pdf.name,
                    "output": summary
                })
