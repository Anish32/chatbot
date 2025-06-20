import streamlit as st
from google import genai
from google.genai import types

# 🔐 Replace with your actual Gemini API key
GEMINI_API_KEY = "AIzaSyBe3fKTMbzrpfTfcGJ6fpQYmwcz9jFR1aI"

# Initialize Gemini client
def init_gemini_client():
    try:
        return genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Failed to initialize Gemini Client: {e}")
        return None

# Get Gemini response
def ask_gemini(prompt, client):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        return response.text.strip()
    except Exception as e:
        return f"❌ Error from Gemini: {e}"

# Streamlit app logic
def main():
    st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖")
    st.title("🤖 Gemini Chatbot")
    st.write("Ask anything and get a response from Google's Gemini AI.")

    client = init_gemini_client()
    if not client:
        return

    # Session state to keep chat history
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # User input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message:")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        response = ask_gemini(user_input, client)
        st.session_state.chat_history.append(("You", user_input))
        st.session_state.chat_history.append(("Gemini", response))
        # Use st.rerun() instead of st.experimental_rerun()
        st.rerun()

    # Display chat history
    for sender, message in reversed(st.session_state.chat_history):
        st.markdown(f"**{sender}:** {message}")

if __name__ == "__main__":
    main()
