import os
import streamlit as st
from groq import Groq

api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are DocuMind AI, a friendly and helpful university document assistant.

You have two modes:

1. GENERAL CONVERSATION — for greetings, small talk, or general questions (hi, hello, how are you, what can you do, thank you, etc.):
   - Respond naturally, warmly, and helpfully.
   - Introduce yourself as DocuMind AI when greeted.
   - Explain you can answer questions about uploaded university documents.

2. DOCUMENT MODE — when the user asks about course content, fees, modules, entry requirements, etc.:
   - Answer using ONLY the provided context from uploaded documents.
   - Always mention the document name and page number your answer comes from.
   - If the answer is not in the context, say: "I could not find this in the uploaded documents."
   - Use markdown formatting (bullet points, bold) where helpful.
"""

# These trigger words mean it's a general/greeting message — skip document search
GENERAL_PHRASES = [
    "hi", "hello", "hey", "howdy", "hiya",
    "how are you", "how r you", "what's up", "whats up",
    "good morning", "good afternoon", "good evening", "good night",
    "thanks", "thank you", "cheers", "bye", "goodbye", "see you",
    "what can you do", "who are you", "what are you", "help",
    "nice", "great", "awesome", "ok", "okay", "cool",
]

def is_general_message(text: str) -> bool:
    """Returns True if the message is a greeting or general chat."""
    cleaned = text.lower().strip().rstrip("!?.")
    # Exact match or starts with a greeting phrase
    for phrase in GENERAL_PHRASES:
        if cleaned == phrase or cleaned.startswith(phrase):
            return True
    # Very short messages (1-2 words) are almost always general
    if len(cleaned.split()) <= 2:
        return True
    return False


def build_user_message(question: str, retrieved_chunks: list) -> str:
    """Combine question + document chunks into one message."""
    if not retrieved_chunks:
        return question  # no context needed for general messages

    context = ""
    for chunk in retrieved_chunks:
        source_type = chunk.get("source_type", "PDF")
        context += f"\n\n[Source: {chunk['file_name']} | Page: {chunk['page_number']} | Type: {source_type}]\n"
        context += chunk["text"]

    return f"Context from uploaded documents:\n{context}\n\n---\n\nQuestion: {question}\n"


def ask_claude(question: str, retrieved_chunks: list, history: list) -> str:
    # Skip document context for general messages
    chunks = [] if is_general_message(question) else retrieved_chunks

    user_message = build_user_message(question, chunks)
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + history
        + [{"role": "user", "content": user_message}]
    )
    response = client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        messages=messages,
    )
    content = response.choices[0].message.content
    return content if content is not None else ""


def ask_claude_streaming(question: str, retrieved_chunks: list, history: list):
    # Skip document context for general messages
    chunks = [] if is_general_message(question) else retrieved_chunks

    user_message = build_user_message(question, chunks)
    messages = (
        [{"role": "system", "content": SYSTEM_PROMPT}]
        + history
        + [{"role": "user", "content": user_message}]
    )
    stream = client.chat.completions.create(
        model=MODEL,
        max_tokens=1024,
        messages=messages,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta is not None:
            yield delta