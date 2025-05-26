import streamlit as st
import openai

# Set up Streamlit page
st.set_page_config(page_title="AI Study Assistant")
st.title("📚 Personal AI Study Assistant")

# Set OpenAI key
openai.api_key = st.secrets["OPENAI_API_KEY"]

# Input from user
user_question = st.text_input("Ask a study-related question:")

if st.button("Get Answer"):
    if user_question.strip() == "":
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",  # or "gpt-4" if your key supports it
                    messages=[
                        {"role": "system", "content": "You are a helpful study assistant."},
                        {"role": "user", "content": user_question}
                    ]
                )
                answer = response.choices[0].message.content
                st.success(answer)
            except Exception as e:
                st.error(f"Error: {e}")
