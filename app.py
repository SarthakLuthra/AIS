import streamlit as st
import requests
import fitz  # PyMuPDF

# Set page config
st.set_page_config(page_title="AI Study Assistant", layout="centered")

# Get API key
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

# Session state for chat and history
if "history" not in st.session_state:
    st.session_state.history = []

# GPT-3 style prompt handler
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

# Extract text from PDF
def extract_text_from_pdf(uploaded_file):
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Title
st.title("📚 Personal AI Study Assistant")

# --- Sidebar History ---
st.sidebar.title("📜 Interaction History")
if st.session_state.history:
    for idx, entry in enumerate(reversed(st.session_state.history), 1):
        st.sidebar.markdown(f"**{idx}. {entry['type']}**")
        st.sidebar.markdown(f"- 🔹 Input: `{entry['input'][:50]}...`")
        st.sidebar.markdown(f"- 🧠 Output: `{entry['output'][:60]}...`")
        st.sidebar.markdown("---")
else:
    st.sidebar.info("No history yet. Start exploring!")

# --- Main Loop ---
while True:
    st.markdown("Choose what you'd like to do:")
    option = st.radio("Select input type:", ("Ask a question", "Upload a PDF"), key="input_choice")

    if option == "Ask a question":
        user_query = st.text_input("❓ Enter your study question:")
        if st.button("Ask"):
            if user_query:
                with st.spinner("Thinking..."):
                    response = ask_together_ai(user_query)
                    st.subheader("🧠 AI Response")
                    st.success(response)

                    # Save to history
                    st.session_state.history.append({
                        "type": "Question",
                        "input": user_query,
                        "output": response
                    })

                    st.experimental_rerun()
            else:
                st.warning("Please enter a question.")

    elif option == "Upload a PDF":
        uploaded_pdf = st.file_uploader("📄 Upload your study PDF", type=["pdf"])
        if uploaded_pdf and st.button("Summarize PDF"):
            with st.spinner("Reading and summarizing..."):
                pdf_text = extract_text_from_pdf(uploaded_pdf)
                if len(pdf_text) > 15000:
                    st.warning("PDF is too long. Summarizing only the first 15000 characters.")
                    pdf_text = pdf_text[:15000]

                summary_prompt = f"Please summarize the following study material:\n\n{pdf_text}"
                summary = ask_together_ai(summary_prompt)
                st.subheader("🧠 Summary")
                st.success(summary)

                # Save to history
                st.session_state.history.append({
                    "type": "PDF Summary",
                    "input": uploaded_pdf.name,
                    "output": summary
                })

                st.experimental_rerun()

    break  # Exit the while loop after one run to allow rerun on interaction

