import streamlit as st
import requests

# Set page configuration for a modern look
st.set_page_config(
    page_title="AI Agent Article Processor",
    page_icon="🤖",
    layout="centered",
)

# UI Elements: Title and Subtitle
st.title("🤖 AI Agent Article Processor")
st.markdown(
    """
Welcome to the **AI Agent Article Processor**!  
This tool automates the process of reading an article, summarizing its key points
using **Google Gemini**, logging the data to a **Google Sheet**, and sending the
summary directly to your **inbox**.
"""
)

st.markdown("---")

# Text Input fields
email = st.text_input(
    "Enter your Email Address", placeholder="e.g., user@example.com"
)
article_url = st.text_input(
    "Enter the Article URL",
    placeholder="e.g., https://en.wikipedia.org/wiki/Lionel_Messi",
)

st.markdown("<br>", unsafe_allow_html=True)

# Action Button
if st.button("Process Article", type="primary", use_container_width=True):
    # 1. Validate that both input fields are not empty
    if not email or not article_url:
        st.warning(
            "⚠️ Please provide both your email address and an article URL before proceeding."
        )
    else:
        # 2. Display a loading spinner while sending the data
        with st.spinner(
            "AI Agent is processing the article... please check your Google Sheet and Inbox shortly!"
        ):
            try:
                # 3. Send a POST request to the local FastAPI backend
                backend_url = "http://localhost:8000/process-article"
                payload = {"email": email, "article_url": article_url}

                response = requests.post(backend_url, json=payload, timeout=15)

                # 4. Handle the server response cleanly
                if response.status_code == 200:
                    response_data = response.json()
                    st.success(
                        f"✅ **Success!** Your article is being processed. "
                        f"(Session ID: `{response_data.get('session_id')}`)"
                    )
                    st.balloons()
                else:
                    error_detail = response.json().get(
                        "detail", "Unknown error occurred."
                    )
                    st.error(f"❌ Failed to process article: {error_detail}")

            except requests.exceptions.ConnectionError:
                st.error(
                    "❌ Could not connect to the backend server. "
                    "Please ensure the FastAPI server is running on http://localhost:8000."
                )
            except Exception as e:
                st.error(f"❌ An unexpected error occurred: {str(e)}")
