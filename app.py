import streamlit as st
from google import genai
from google.genai import types
import os
import datetime
import json # Import json to save data in a structured format

# Access API key - REPLACE WITH YOUR ACTUAL KEY
GEMINI_API_KEY = "AIzaSyBe3fKTMbzrpfTfcGJ6fpQYmwcz9jFR1aI" # Use your actual API key

# Define the filename for automatic saving
# Using a fixed filename makes it easier to overwrite and keep the latest state
AUTO_SAVE_FILENAME = "chat_history_auto.json"

# Initialize Gemini client
@st.cache_resource
def init_gemini_client(api_key):
    try:
        if not api_key or api_key == "YOUR_API_KEY":
             st.error("API Key is not set. Please replace 'YOUR_API_KEY' with your actual key in app.py or use Colab Secrets.")
             return None
        return genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialize Gemini Client: {e}")
        st.error("Please ensure your API key is correctly set and is a valid API key.")
        return None

# Get Gemini response
def ask_gemini(prompt, client):
    if client is None:
        return "❌ Gemini client is not initialized due to missing or invalid API key."
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            ),
        )
        if hasattr(response, 'text'):
             return response.text.strip()
        else:
             print(f"Received unexpected response structure: {response}")
             return "❌ Received an unexpected response from Gemini."

    except Exception as e:
        if hasattr(e, 'error_details'):
            return f"❌ Error from Gemini API: {e.error_details}"
        else:
            return f"❌ An unexpected error occurred while calling Gemini: {e}"

# Function to save chat history automatically
def auto_save_chat_history(chat_history, filename=AUTO_SAVE_FILENAME):
    if not chat_history:
        print(f"No chat history to save to {filename}.") # Added print statement
        return

    try:
        with open(filename, "w") as f:
            json.dump(chat_history, f, indent=4)
        print(f"Chat history successfully auto-saved to {filename}.") # Added print statement
        # Consider adding a small message in the Streamlit UI, maybe in the sidebar
        # st.sidebar.info("Chat history auto-saved.")
    except Exception as e:
        st.error(f"Error auto-saving chat history: {e}")
        print(f"Error auto-saving chat history to {filename}: {e}") # Added print statement

# Function to load chat history automatically when the app starts
def load_chat_history(filename=AUTO_SAVE_FILENAME):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                chat_history = json.load(f)
            st.sidebar.success("Chat history loaded.")
            print(f"Chat history loaded from {filename}.") # Added print statement
            return chat_history
        except Exception as e:
            st.error(f"Error loading chat history: {e}")
            print(f"Error loading chat history from {filename}: {e}") # Added print statement
            return []
    else:
        print(f"No existing chat history file found at {filename}.") # Added print statement
    return []


# Streamlit app logic
def main():
    st.set_page_config(page_title="Gemini Chatbot", page_icon="🤖")
    st.title("🤖 Gemini Chatbot")
    st.write("Ask anything and get a response from Google's Gemini AI.")

    client = init_gemini_client(GEMINI_API_KEY)

    if client is None:
        return

    # Session state to keep chat history across reruns
    # Load history when the session starts if it exists
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = load_chat_history()

    # User input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Your message:", key="user_input")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Get Gemini response
        response = ask_gemini(user_input, client)

        # Add Gemini response to history
        st.session_state.chat_history.append({"role": "gemini", "content": response})

        # Auto-save the chat history after each interaction
        auto_save_chat_history(st.session_state.chat_history)

        # Rerun the app to display the updated chat history
        st.rerun()

    # Display chat history
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.markdown(f"**You:** {message['content']}")
        elif message["role"] == "gemini":
            st.markdown(f"**Gemini:** {message['content']}")

    # Optional: Manual save button (can keep this alongside auto-save if desired)
    # if st.button("Manual Save Chat History"):
    #     # Using a different filename for manual saves
    #     timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    #     manual_filename = f"chat_history_{timestamp}.json"
    #     try:
    #         with open(manual_filename, "w") as f:
    #              json.dump(st.session_state.chat_history, f, indent=4)
    #         st.success(f"Chat history manually saved to {manual_filename}")
    #     except Exception as e:
    #         st.error(f"Error manually saving chat history: {e}")

    # Optional: Clear chat history and auto-save file button
    if st.button("Clear Chat and Saved File"):
        st.session_state.chat_history = []
        if os.path.exists(AUTO_SAVE_FILENAME):
            try:
                os.remove(AUTO_SAVE_FILENAME)
                print(f"Auto-save file {AUTO_SAVE_FILENAME} removed.") # Added print statement
            except Exception as e:
                print(f"Error removing auto-save file {AUTO_SAVE_FILENAME}: {e}") # Added print statement
        st.success("Chat history cleared and auto-save file removed.")
        st.rerun()


if __name__ == "__main__":
    main()
