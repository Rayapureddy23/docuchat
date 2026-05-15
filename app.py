"""
DocuMind AI — Main Streamlit App
Combines Steps 1–6:
  Step 1 — Claude API (real LLM)
  Step 2 — Conversation history passed to every API call
  Step 3 — RAG pipeline (PDF + HTML ingestion, FAISS search)
  Step 4 — SQLite persistent chat history
  Step 5 — Streaming responses (token by token)
  Step 6 — Deployable to Streamlit Cloud (no Colab dependency)

Run locally:
    streamlit run app.py

Deploy to Streamlit Cloud:
    1. Push this folder to a GitHub repo
    2. Go to share.streamlit.io → New app → select your repo
    3. Add ANTHROPIC_API_KEY in the Secrets panel
    Done. Your app is live.
"""

import streamlit as st
import os

# Our own modules
import database as db
import rag
from llm import ask_claude_streaming

# ---------------------------------------------------------------------------
# Page config — must be the very first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# One-time setup — initialise DB, try loading a saved index
# ---------------------------------------------------------------------------
db.init_db()
if "index_loaded" not in st.session_state:
    st.session_state.index_loaded = rag.load_index_from_disk()

# ---------------------------------------------------------------------------
# SIDEBAR — conversations + file upload
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## DocuMind AI")
    st.caption("Ask questions about your uploaded documents")

    # New chat button
    if st.button("＋  New chat", use_container_width=True):
        new_id = db.create_conversation()
        st.session_state.conversation_id = new_id
        st.rerun()

    st.divider()

    # --- STEP 4: List all saved conversations ---
    conversations = db.list_conversations()
    if conversations:
        st.markdown("**Recent chats**")
        for conv in conversations:
            col1, col2 = st.columns([5, 1])
            is_active = st.session_state.get("conversation_id") == conv["id"]
            label = ("▶ " if is_active else "") + conv["title"]
            with col1:
                if st.button(label, key=f"conv_{conv['id']}", use_container_width=True):
                    st.session_state.conversation_id = conv["id"]
                    st.rerun()
            with col2:
                if st.button("🗑", key=f"del_{conv['id']}"):
                    db.delete_conversation(conv["id"])
                    if st.session_state.get("conversation_id") == conv["id"]:
                        del st.session_state["conversation_id"]
                    st.rerun()

    st.divider()

    # --- STEP 3: File upload ---
    st.markdown("**Upload documents**")
    uploaded_files = st.file_uploader(
        "PDF or HTML files",
        type=["pdf", "html", "htm"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if st.button("Build index", use_container_width=True, type="primary"):
        if not uploaded_files:
            st.warning("Please upload at least one file first.")
        else:
            # Save uploaded files to disk so rag.py can read them
            saved_paths = []
            os.makedirs("data/uploads", exist_ok=True)
            for f in uploaded_files:
                path = os.path.join("data/uploads", f.name)
                with open(path, "wb") as out:
                    out.write(f.getbuffer())
                saved_paths.append(path)

            with st.spinner("Processing documents..."):
                result = rag.build_index(saved_paths)

            st.session_state.index_loaded = True
            st.success(f"Ready — {result['total_chunks']} chunks from {result['total_files']} files")

    # Show index status
    status = rag.get_status()
    if status["loaded"]:
        st.caption(f"Index: {status['total_chunks']} chunks • {len(status['files'])} file(s)")
        with st.expander("Files in index"):
            for fname in status["files"]:
                st.caption(f"• {fname}")
    else:
        st.caption("No index loaded — upload files above")

# ---------------------------------------------------------------------------
# MAIN AREA — chat interface
# ---------------------------------------------------------------------------

# Make sure we always have an active conversation
if "conversation_id" not in st.session_state:
    if conversations:
        st.session_state.conversation_id = conversations[0]["id"]
    else:
        new_id = db.create_conversation()
        st.session_state.conversation_id = new_id

conversation_id = st.session_state.conversation_id

# --- STEP 4: Load messages from DB ---
messages = db.load_messages(conversation_id)

# Display title
conv_list = db.list_conversations()
current_conv = next((c for c in conv_list if c["id"] == conversation_id), None)
if current_conv:
    st.markdown(f"### {current_conv['title']}")

# Render all past messages (with markdown for formatting and code blocks)
for msg in messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Chat input at the bottom
# ---------------------------------------------------------------------------
user_input = st.chat_input(
    "Ask about your documents...",
    disabled=not status["loaded"],
)

if not status["loaded"]:
    st.info("Upload documents in the sidebar and click **Build index** to start chatting.")

if user_input:
    # Show the user's message immediately
    with st.chat_message("user"):
        st.markdown(user_input)

    # STEP 4 — save user message to DB
    db.save_message(conversation_id, "user", user_input)

    # Auto-title the conversation after the first question
    if db.get_message_count(conversation_id) == 1:
        db.auto_title(conversation_id, user_input)

    # STEP 3 — retrieve relevant document chunks
    retrieved_chunks = rag.search(user_input, top_k=5)

    # STEP 2 — load full conversation history to pass to Claude
    history = db.load_messages(conversation_id)
    # The last message is the one we just saved (user's question with context),
    # but we send the original question to the UI and the enriched version to the API.
    # Remove the last item — we'll build a richer version below via ask_claude_streaming.
    history_for_api = history[:-1]  # everything except the message we just saved

    # STEP 5 — stream the response token-by-token
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        for chunk in ask_claude_streaming(user_input, retrieved_chunks, history_for_api):
            full_response += chunk
            response_placeholder.markdown(full_response + "▌")  # blinking cursor effect

        response_placeholder.markdown(full_response)  # final render without cursor

        # Show sources below the answer
        if retrieved_chunks:
            with st.expander("Sources used", expanded=False):
                for i, src in enumerate(retrieved_chunks):
                    st.markdown(
                        f"**{i+1}. {src['file_name']}** — "
                        f"Page {src['page_number']} "
                        f"*(relevance distance: {src['distance']:.2f})*"
                    )
                    st.caption(src["text"][:300] + "...")

    # STEP 4 — save assistant response to DB
    db.save_message(conversation_id, "assistant", full_response)

    # Rerun to refresh the sidebar conversation list with updated title
    st.rerun()