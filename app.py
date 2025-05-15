import streamlit as st
import openai

# Set page title
st.set_page_config(page_title="AI Study Assistant")

# Load API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Title
st.title("📚 Personal AI Study Assistant")

# Input box
user_question = st.text_input("Ask a study-related question:")

# Button
if st.button("Get Answer"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = openai.Completion.create(
                    engine="text-davinci-003",
                    prompt=user_question,
                    max_tokens=150,
                    temperature=0.7
                )
                st.success(response.choices[0].text.strip())
            except Exception as e:
                st.error(f"Error: {e}")
