import os
import streamlit as st
from groq import Groq

api_key = st.secrets.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = """You are DocuMind AI, a helpful university document assistant.
Answer questions using ONLY the context retrieved from uploaded university documents.
If the answer is not in the context, say: "I could not find this in the uploaded documents."
Always mention which document and page number your answer comes from.
Use markdown formatting where helpful.
"""

def build_user_message(question: str, retrieved_chunks: list) -> str:
    context = ""
    for chunk in retrieved_chunks:
        source_type = chunk.get("source_type", "PDF")
        context += f"\n\n[Source: {chunk['file_name']} | Page: {chunk['page_number']} | Type: {source_type}]\n"
        context += chunk["text"]
    return f"Context from uploaded documents:\n{context}\n\n---\n\nQuestion: {question}\n"

def ask_claude(question: str, retrieved_chunks: list, history: list) -> str:
    user_message = build_user_message(question, retrieved_chunks)
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
    return content or ""

def ask_claude_streaming(question: str, retrieved_chunks: list, history: list):
    user_message = build_user_message(question, retrieved_chunks)
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