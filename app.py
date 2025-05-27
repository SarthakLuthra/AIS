import streamlit as st
import requests
import fitz  # PyMuPDF

# --- CONFIG ---
st.set_page_config(page_title="AI Study Assistant", layout="centered")

TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

# Initialize history
if "history" not in st.session_state:
    st.session_state.history = []

# Function: Ask Together AI
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

# Function: Extract PDF text
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    return "\n".join(page.get_text() for page in doc)

# --- MAIN APP ---
st.title("📚 Personal AI Study Assistant")

# Display full history (like a chat)
for item in st.session_state.history:
    if item["type"] == "Question":
        st.markdown(f"**🧑 You asked:** {item['input']}")
        st.markdown(f"**🤖 AI answered:** {item['output']}")
    elif item["type"] == "PDF Summary":
        st.markdown(f"**📄 You uploaded:** {item['input']}")
        st.markdown(f"**📌 Summary:** {item['output']}")
    st.divider()

# Tabs for question or PDF upload
tab1, tab2 = st.tabs(["❓ Ask a Question", "📄 Upload a PDF"])

# --- Question Tab ---
with tab1:
    user_query = st.text_input("Enter your question:")
    if st.button("Submit Question"):
        if user_query.strip() != "":
            with st.spinner("Thinking..."):
                response = ask_together_ai(user_query)
                st.session_state.history.append({
                    "type": "Question",
                    "input": user_query,
                    "output": response
                })
                st.markdown(f"**🧑 You asked:** {user_query}")
                st.markdown(f"**🤖 AI answered:** {response}")
                st.divider()

        else:
            st.warning("Please enter a question.")

# --- PDF Tab ---
with tab2:
    uploaded_pdf = st.file_uploader("Upload your study PDF", type=["pdf"])
    if uploaded_pdf and st.button("Summarize PDF"):
        with st.spinner("Reading and summarizing..."):
            pdf_text = extract_text_from_pdf(uploaded_pdf)
            if len(pdf_text) > 15000:
                pdf_text = pdf_text[:15000]
                st.info("PDF too long. Summarizing the first 15000 characters.")
            summary = ask_together_ai(f"Please summarize the following study material:\n\n{pdf_text}")
            st.session_state.history.append({
                "type": "PDF Summary",
                "input": uploaded_pdf.name,
                "output": summary
            })
            st.markdown(f"**📄 You uploaded:** {uploaded_pdf.name}")
            st.markdown(f"**📌 Summary:** {summary}")
            st.divider()

