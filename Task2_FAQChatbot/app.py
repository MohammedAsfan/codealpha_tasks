import csv
import math
import re
from collections import Counter

import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="FAQ Assistant",
    page_icon="🤖",
    layout="centered"
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #f8fbff 0%,
        #eef5ff 50%,
        #f8fbff 100%
    );
}

.block-container {
    max-width: 900px;
    padding-top: 2rem;
    padding-bottom: 3rem;
}

.hero {
    text-align: center;
    padding: 25px 10px;
}

.hero-title {
    font-size: 3rem;
    font-weight: 800;
    color: #172033;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #667085;
}

.badge {
    display: inline-block;
    margin-top: 12px;
    padding: 6px 14px;
    border-radius: 20px;
    background: #e8f1ff;
    color: #2864d7;
    font-weight: 600;
    font-size: 0.85rem;
}

.feature {
    text-align: center;
    background: white;
    border: 1px solid #e4e9f2;
    border-radius: 14px;
    padding: 15px;
    margin-top: 15px;
}

.feature-icon {
    font-size: 1.6rem;
}

.feature-title {
    font-weight: 700;
    color: #172033;
}

.feature-text {
    font-size: 0.8rem;
    color: #667085;
}

.footer {
    text-align: center;
    color: #98a2b3;
    font-size: 0.85rem;
    margin-top: 30px;
}

div.stButton > button {
    border-radius: 12px;
    min-height: 45px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# TEXT PREPROCESSING
# =========================================================

def preprocess_text(text):

    stop_words = {
        "what", "is", "the", "a", "an", "do", "does",
        "how", "can", "i", "you", "we", "are", "to",
        "of", "for", "in", "on", "and", "or", "my",
        "your", "about", "today", "please", "tell", "me"
    }

    text = text.lower()

    text = re.sub(
        r"[^a-z0-9\s]",
        "",
        text
    )

    words = text.split()

    words = [
        word
        for word in words
        if word not in stop_words
    ]

    return " ".join(words)


# =========================================================
# LOAD FAQ DATA
# =========================================================

@st.cache_data
def load_faq_data():

    faq_list = []

    with open(
        "faq_data.csv",
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            faq_list.append({
                "question": row["question"],
                "answer": row["answer"],
                "clean_question": preprocess_text(
                    row["question"]
                )
            })

    return faq_list


faq_data = load_faq_data()


# =========================================================
# TF-IDF
# =========================================================

def create_vocabulary(documents):

    vocabulary = set()

    for document in documents:

        words = document.split()

        for word in words:
            vocabulary.add(word)

    return sorted(vocabulary)


def calculate_idf(documents, vocabulary):

    total_documents = len(documents)

    idf = {}

    for word in vocabulary:

        document_count = sum(
            1
            for document in documents
            if word in document.split()
        )

        idf[word] = math.log(
            (total_documents + 1) /
            (document_count + 1)
        ) + 1

    return idf


def calculate_tfidf(text, vocabulary, idf):

    words = text.split()

    word_counts = Counter(words)

    total_words = len(words)

    vector = []

    for word in vocabulary:

        tf = word_counts[word] / total_words if total_words else 0

        vector.append(
            tf * idf[word]
        )

    return vector


# =========================================================
# COSINE SIMILARITY
# =========================================================

def cosine_similarity(vector_a, vector_b):

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    magnitude_a = math.sqrt(
        sum(a * a for a in vector_a)
    )

    magnitude_b = math.sqrt(
        sum(b * b for b in vector_b)
    )

    if magnitude_a == 0 or magnitude_b == 0:
        return 0

    return dot_product / (
        magnitude_a * magnitude_b
    )


# =========================================================
# BUILD TF-IDF MODEL
# =========================================================

documents = [
    faq["clean_question"]
    for faq in faq_data
]

vocabulary = create_vocabulary(documents)

idf = calculate_idf(
    documents,
    vocabulary
)

faq_vectors = [
    calculate_tfidf(
        faq["clean_question"],
        vocabulary,
        idf
    )
    for faq in faq_data
]


# =========================================================
# FIND BEST FAQ
# =========================================================

def find_best_answer(user_question):

    cleaned_question = preprocess_text(
        user_question
    )

    user_vector = calculate_tfidf(
        cleaned_question,
        vocabulary,
        idf
    )

    scores = [
        cosine_similarity(
            user_vector,
            faq_vector
        )
        for faq_vector in faq_vectors
    ]

    best_index = scores.index(
        max(scores)
    )

    best_score = scores[best_index]

    return (
        faq_data[best_index]["question"],
        faq_data[best_index]["answer"],
        best_score
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    """
    <div class="hero">
        <div class="hero-title">🤖 FAQ Assistant</div>
        <div class="hero-subtitle">
            Ask a question and get the most relevant answer
        </div>
        <div class="badge">
            ✨ NLP-Powered Chatbot
        </div>
    </div>
    """,
    unsafe_allow_html=True
)


# =========================================================
# CHAT HISTORY
# =========================================================

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


for message in st.session_state.chat_history:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if (
            message["role"] == "assistant"
            and "confidence" in message
        ):
            st.caption(
                f"Match confidence: "
                f"{message['confidence']:.1%}"
            )


# =========================================================
# USER INPUT
# =========================================================

user_question = st.chat_input(
    "Ask your question..."
)


# =========================================================
# PROCESS QUESTION
# =========================================================

if user_question:

    st.session_state.chat_history.append({
        "role": "user",
        "content": user_question
    })

    matched_question, answer, score = (
        find_best_answer(user_question)
    )

    if score < 0.25:

        response = (
            "Sorry, I couldn't find a relevant "
            "answer to your question. Please "
            "try asking in a different way."
        )

    else:

        response = answer

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response,
        "confidence": score
    })

    st.rerun()


# =========================================================
# CLEAR CHAT
# =========================================================

if st.session_state.chat_history:

    if st.button("🗑️ Clear Chat"):

        st.session_state.chat_history = []

        st.rerun()


# =========================================================
# HOW IT WORKS
# =========================================================

st.write("")

st.subheader("How it works")

f1, f2, f3 = st.columns(3)

with f1:

    st.markdown("""
    <div class="feature">
        <div class="feature-icon">🧹</div>
        <div class="feature-title">
            Text Cleaning
        </div>
        <div class="feature-text">
            Questions are cleaned and normalized.
        </div>
    </div>
    """, unsafe_allow_html=True)


with f2:

    st.markdown("""
    <div class="feature">
        <div class="feature-icon">🔢</div>
        <div class="feature-title">
            TF-IDF
        </div>
        <div class="feature-text">
            Text is converted into numerical vectors.
        </div>
    </div>
    """, unsafe_allow_html=True)


with f3:

    st.markdown("""
    <div class="feature">
        <div class="feature-icon">🎯</div>
        <div class="feature-title">
            Cosine Similarity
        </div>
        <div class="feature-text">
            Finds the closest matching FAQ.
        </div>
    </div>
    """, unsafe_allow_html=True)


# =========================================================
# FOOTER
# =========================================================

st.markdown(
    """
    <div class="footer">
        FAQ Assistant • CodeAlpha Artificial Intelligence Internship<br>
        Built with Python • Streamlit • TF-IDF • Cosine Similarity
    </div>
    """,
    unsafe_allow_html=True
)