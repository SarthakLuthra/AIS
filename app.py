import streamlit as st
import requests

# Use the Together API key from Streamlit Secrets
TOGETHER_API_KEY = st.secrets["TOGETHER_API_KEY"]

def ask_together_ai(question):
    url = "https://api.together.xyz/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {TOGETHER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "messages": [
            {"role": "system", "content": "You are a helpful study assistant."},
            {"role": "user", "content": question}
        ],
        "temperature": 0.7
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]

# Streamlit App UI
st.set_page_config(page_title="AI Study Assistant")
st.title("📚 Personal AI Study Assistant")

user_question = st.text_input("Ask a study-related question:")

if st.button("Get Answer"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                answer = ask_together_ai(user_question)
                st.success(answer)
            except Exception as e:
                st.error(f"Error: {e}")
