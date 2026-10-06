import os
import time
import json
import html
from textwrap import dedent

import streamlit as st
import streamlit.components.v1 as components
from google import genai


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LinguaAI - Language Translator",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    /* Main page */
    .stApp {
        background: linear-gradient(
            135deg,
            #f8fbff 0%,
            #eef5ff 50%,
            #f8fbff 100%
        );
    }

    /* Main content width */
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Header */
    .hero {
        text-align: center;
        padding: 25px 10px 15px 10px;
    }

    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        margin-bottom: 5px;
        color: #172033;
    }

    .hero-subtitle {
        font-size: 1.1rem;
        color: #667085;
        margin-bottom: 10px;
    }

    .badge {
        display: inline-block;
        padding: 6px 14px;
        border-radius: 20px;
        background: #e8f1ff;
        color: #2864d7;
        font-size: 0.85rem;
        font-weight: 600;
        margin-top: 8px;
    }

    /* Translation cards */
    .translation-card {
        background: white;
        border-radius: 18px;
        padding: 24px;
        margin-top: 15px;
        border: 1px solid #e4e9f2;
        box-shadow: 0 8px 25px rgba(30, 60, 100, 0.07);
    }

    .card-title {
        font-size: 1rem;
        font-weight: 700;
        color: #344054;
        margin-bottom: 8px;
    }

    /* Result box */
    .result-box {
        background: #f8fbff;
        border: 1px solid #d9e5f7;
        border-radius: 14px;
        padding: 20px;
        min-height: 120px;
        font-size: 1.1rem;
        line-height: 1.7;
        color: #172033;
    }

    /* Feature cards */
    .feature {
        text-align: center;
        background: white;
        border: 1px solid #e4e9f2;
        border-radius: 16px;
        padding: 18px;
        margin-top: 15px;
        box-shadow: 0 5px 18px rgba(30, 60, 100, 0.05);
    }

    .feature-icon {
        font-size: 1.7rem;
    }

    .feature-title {
        font-weight: 700;
        margin-top: 5px;
        color: #172033;
    }

    .feature-text {
        font-size: 0.85rem;
        color: #667085;
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #98a2b3;
        font-size: 0.85rem;
        padding-top: 25px;
    }

    /* Buttons */
    div.stButton > button {
        border-radius: 12px;
        min-height: 46px;
        font-weight: 600;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# API CONFIGURATION
# =========================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    st.error("Gemini API key not found.")
    st.info(
        "Set GEMINI_API_KEY in your terminal and restart Streamlit."
    )
    st.stop()

client = genai.Client(api_key=api_key)


# =========================================================
# LANGUAGE CONFIGURATION
# =========================================================

languages = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Kannada": "kn",
    "Telugu": "te",
    "Malayalam": "ml",
    "Bengali": "bn",
    "Marathi": "mr",
    "Gujarati": "gu",
    "French": "fr",
    "German": "de",
    "Spanish": "es",
    "Japanese": "ja",
    "Korean": "ko",
    "Arabic": "ar"
}

language_list = list(languages.keys())


# =========================================================
# SESSION STATE
# =========================================================

if "source_language" not in st.session_state:
    st.session_state.source_language = "English"

if "target_language" not in st.session_state:
    st.session_state.target_language = "Hindi"

if "translation" not in st.session_state:
    st.session_state.translation = ""

if "input_text" not in st.session_state:
    st.session_state.input_text = ""


# =========================================================
# HEADER
# =========================================================

st.markdown(
    dedent("""
    <div class="hero">
        <div class="hero-title">
            🌐 LinguaAI
        </div>
        <div class="hero-subtitle">
            Intelligent multilingual translation powered by Google Gemini
        </div>
        <div class="badge">
            ✨ AI-Powered Translation
        </div>
    </div>
    """),
    unsafe_allow_html=True
)


# =========================================================
# LANGUAGE SELECTION + SWAP
# =========================================================

col1, swap_col, col2 = st.columns([5, 1, 5])

with col1:
    source_language = st.selectbox(
        "From",
        language_list,
        index=language_list.index(
            st.session_state.source_language
        )
    )

with swap_col:
    st.write("")
    st.write("")

    if st.button(
        "⇄",
        help="Swap source and target languages"
    ):
        old_source = st.session_state.source_language
        old_target = st.session_state.target_language

        st.session_state.source_language = old_target
        st.session_state.target_language = old_source

        st.rerun()

with col2:
    target_language = st.selectbox(
        "To",
        language_list,
        index=language_list.index(
            st.session_state.target_language
        )
    )


# Update session state with current selections
st.session_state.source_language = source_language
st.session_state.target_language = target_language


# Keep session state synchronized
st.session_state.source_language = source_language
st.session_state.target_language = target_language


# =========================================================
# INPUT SECTION
# =========================================================

st.markdown(
    '<div class="card-title">✍️ Enter your text</div>',
    unsafe_allow_html=True
)

text = st.text_area(
    "Text to translate",
    value=st.session_state.input_text,
    placeholder="Type or paste your text here...",
    height=190,
    label_visibility="collapsed"
)

st.session_state.input_text = text

# Character count
st.caption(f"{len(text)} characters")

if st.button("🗑️ Clear text"):
    st.session_state.input_text = ""
    st.session_state.translation = ""
    st.rerun()


# =========================================================
# TRANSLATE FUNCTION
# =========================================================

if st.button(
    "🌐  Translate",
    use_container_width=True
):

    if not text.strip():

        st.warning("Please enter some text first.")

    elif source_language == target_language:

        st.session_state.translation = text
        st.info("Source and target languages are the same.")

    else:

        prompt = f"""
You are an expert professional translator.

Translate the following text from {source_language}
to {target_language}.

IMPORTANT RULES:

1. Return ONLY the translated text.
2. Do not provide explanations.
3. Do not add quotation marks.
4. Preserve the original meaning.
5. Preserve names, numbers and punctuation.
6. Use the correct native writing system for {target_language}.
7. Do NOT transliterate the translation into English letters.
8. Produce natural, fluent and grammatically correct {target_language}.
9. Preserve paragraphs and line breaks where appropriate.

Source language:
{source_language}

Target language:
{target_language}

Text:
{text}
"""

        models_to_try = [
            "gemini-3.5-flash",
            "gemini-3.6-flash",
            "gemini-3.8-flash"
        ]

        translation = None
        last_error = None

        with st.spinner("✨ AI is translating..."):

            for model_name in models_to_try:

                for attempt in range(2):

                    try:

                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt
                        )

                        translation = response.text.strip()

                        if translation:
                            break

                    except Exception as e:

                        last_error = str(e)

                        # Retry temporary server errors
                        if "503" in last_error or "UNAVAILABLE" in last_error:

                            if attempt == 0:
                                time.sleep(2)
                                continue

                        break

                if translation:
                    break

        if translation:

            st.session_state.translation = translation

        else:

            st.error(
                "Translation service is temporarily unavailable. "
                "Please try again in a moment."
            )




# =========================================================
# TRANSLATION RESULT
# =========================================================

if st.session_state.translation:

    translation = st.session_state.translation

    st.markdown(
        '<div class="translation-card">',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="card-title">✨ Translation</div>',
        unsafe_allow_html=True
    )

    # Display result
    st.markdown(
        f"""
        <div class="result-box">
            {html.escape(translation).replace(chr(10), "<br>")}
        </div>
        """,
        unsafe_allow_html=True
    )

    st.write("")

    # Action buttons
    action1, action2, action3 = st.columns(3)

    # -----------------------------------------------------
    # Copy button
    # -----------------------------------------------------

    with action1:

        copy_text = json.dumps(translation)

        components.html(
            f"""
            <button
                onclick='navigator.clipboard.writeText({copy_text})'
                style="
                    width:100%;
                    padding:12px;
                    border:none;
                    border-radius:10px;
                    background:#eef4ff;
                    color:#2457c5;
                    font-weight:600;
                    cursor:pointer;
                "
            >
                📋 Copy
            </button>
            """,
            height=50
        )

    # -----------------------------------------------------
    # Text to speech
    # -----------------------------------------------------

    with action2:

        speech_language = languages[target_language]

        speech_text = json.dumps(translation)

        components.html(
            f"""
            <button
                onclick='
                    const text = {speech_text};
                    const utterance = new SpeechSynthesisUtterance(text);
                    utterance.lang = "{speech_language}";
                    speechSynthesis.cancel();
                    speechSynthesis.speak(utterance);
                '
                style="
                    width:100%;
                    padding:12px;
                    border:none;
                    border-radius:10px;
                    background:#eef4ff;
                    color:#2457c5;
                    font-weight:600;
                    cursor:pointer;
                "
            >
                🔊 Listen
            </button>
            """,
            height=50
        )

    # -----------------------------------------------------
    # Download
    # -----------------------------------------------------

    with action3:

        st.download_button(
            "⬇️ Download",
            data=translation,
            file_name="translation.txt",
            mime="text/plain",
            use_container_width=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


# =========================================================
# FEATURES
# =========================================================

st.write("")
st.subheader("Why LinguaAI?")

f1, f2, f3, f4 = st.columns(4)

with f1:
    st.markdown("""
    <div class="feature">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">AI Powered</div>
        <div class="feature-text">
            Uses Gemini for intelligent translation.
        </div>
    </div>
    """, unsafe_allow_html=True)

with f2:
    st.markdown("""
    <div class="feature">
        <div class="feature-icon">🌍</div>
        <div class="feature-title">15 Languages</div>
        <div class="feature-text">
            Translate between multiple global languages.
        </div>
    </div>
    """, unsafe_allow_html=True)

with f3:
    st.markdown("""
    <div class="feature">
        <div class="feature-icon">🔊</div>
        <div class="feature-title">Text to Speech</div>
        <div class="feature-text">
            Listen to translated text instantly.
        </div>
    </div>
    """, unsafe_allow_html=True)

with f4:
    st.markdown("""
    <div class="feature">
        <div class="feature-icon">⚡</div>
        <div class="feature-title">Fast</div>
        <div class="feature-text">
            Simple and responsive translation workflow.
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div class="footer">

    LinguaAI • CodeAlpha Artificial Intelligence Internship Project<br>
    Built with Python • Streamlit • Google Gemini API

</div>
""", unsafe_allow_html=True)