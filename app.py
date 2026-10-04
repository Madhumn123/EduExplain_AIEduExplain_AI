import streamlit as st
from google import genai
from google.genai import types
from twilio.rest import Client

from prompts import SYSTEM_PROMPT


# -----------------------------
# Page settings
# -----------------------------

st.set_page_config(
    page_title="EduExplain AI",
    page_icon="📚"
)

st.title("📚 EduExplain AI")
st.write("Upload a textbook page and understand it easily.")


# -----------------------------
# API keys
# -----------------------------

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

TWILIO_ACCOUNT_SID = st.secrets["TWILIO_ACCOUNT_SID"]
TWILIO_AUTH_TOKEN = st.secrets["TWILIO_AUTH_TOKEN"]
TWILIO_SMS_FROM = st.secrets["TWILIO_SMS_FROM"]


# -----------------------------
# Gemini
# -----------------------------

gemini = genai.Client(
    api_key=GEMINI_API_KEY
)


# -----------------------------
# Student settings
# -----------------------------

name = st.text_input(
    "Your name",
    placeholder="Enter your name"
)

phone = st.text_input(
    "Phone number",
    placeholder="+91XXXXXXXXXX"
)

level = st.selectbox(
    "🎯 Explain Like",
    [
        "Beginner",
        "8th Standard",
        "10th Standard",
        "College Student",
        "Interview Preparation"
    ]
)


# -----------------------------
# Upload textbook page
# -----------------------------

image = st.file_uploader(
    "📷 Upload textbook page",
    type=["jpg", "jpeg", "png"]
)


# -----------------------------
# Explain button
# -----------------------------

if image:

    st.image(
        image,
        caption="Your textbook page",
        use_container_width=True
    )

    if st.button(
        "🧠 Explain This Page",
        type="primary"
    ):

        image_bytes = image.getvalue()

        prompt = f"""
        {SYSTEM_PROMPT}

        Explain Like level:
        {level}

        Give:

        1. 📖 Simple Explanation
        2. ⭐ Key Points
        3. 💡 Easy Way to Remember
        4. 📝 Short Summary
        5. ❓ 5 Questions and Answers
        6. 🧠 5 MCQs

        Keep the explanation easy to understand.
        """

        with st.spinner("🧠 Reading the textbook..."):

            response = gemini.models.generate_content(
                model="gemini-3.5-flash",
                contents=[
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=image.type
                    ),
                    prompt
                ]
            )

        answer = response.text

        st.session_state["answer"] = answer

        st.subheader("📖 Explanation")

        st.markdown(answer)


# -----------------------------
# Kannada
# -----------------------------

if "answer" in st.session_state:

    if st.button("🗣️ Explain in Kannada"):

        with st.spinner("Preparing Kannada explanation..."):

            response = gemini.models.generate_content(
                model="gemini-3.5-flash",
                contents=[
                    """
                    Explain the following textbook explanation
                    in simple Kannada.

                    Keep important technical terms in English
                    inside brackets.

                    Textbook explanation:
                    """,
                    st.session_state["answer"]
                ]
            )

        st.session_state["kannada"] = response.text

        st.subheader("🗣️ Kannada Explanation")

        st.markdown(response.text)


# -----------------------------
# Ask question
# -----------------------------

if "answer" in st.session_state:

    question = st.chat_input(
        "💬 Ask a question about this page..."
    )

    if question:

        st.chat_message("user").write(question)

        with st.spinner("🤔 Thinking..."):

            response = gemini.models.generate_content(
                model="gemini-3.5-flash",
                contents=[
                    SYSTEM_PROMPT,

                    f"""
                    Here is the textbook explanation:

                    {st.session_state["answer"]}

                    Student question:

                    {question}

                    Answer in simple language.
                    """
                ]
            )

        st.chat_message("assistant").write(
            response.text
        )


# -----------------------------
# Send SMS
# -----------------------------

if "answer" in st.session_state:

    if st.button("📱 Send Summary by SMS"):

        if not phone:

            st.warning(
                "Please enter your phone number."
            )

        else:

            with st.spinner("Preparing SMS..."):

                response = gemini.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=[
                        """
                        Make a very short revision summary
                        of this textbook explanation.

                        Include:
                        - Topic
                        - 3 important points
                        - Short summary
                        - One memory tip

                        Keep it short enough for SMS.

                        Text:
                        """,
                        st.session_state["answer"]
                    ]
                )

            summary = response.text

            try:

                twilio = Client(
                    TWILIO_ACCOUNT_SID,
                    TWILIO_AUTH_TOKEN
                )

                message = twilio.messages.create(
                    body=f"""
EduExplain AI 📚

Hi {name}!

{summary}
""",
                    from_=TWILIO_SMS_FROM,
                    to=phone
                )

                st.success(
                    "📱 Summary sent successfully!"
                )

            except Exception as error:

                st.error(
                    f"Couldn't send SMS: {error}"
                )