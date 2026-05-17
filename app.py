"""
DocuMind AI — Full themed UI matching the DocuMind mockup design
Clean white + blue design with custom CSS injection
"""

import streamlit as st
import os

import database as db
import rag
from llm import ask_claude_streaming

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# THEME — inject CSS to match the DocuMind design mockup
# ---------------------------------------------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}

/* ── App background ── */
.stApp {
    background: #F0F4FF;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #FFFFFF !important;
    border-right: 1px solid #E5E9F5 !important;
    box-shadow: 2px 0 12px rgba(26,86,219,0.06);
}
[data-testid="stSidebar"] > div {
    padding: 0 !important;
}
[data-testid="stSidebarContent"] {
    padding: 1.5rem 1.2rem !important;
}

/* ── Sidebar brand header ── */
.brand-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 6px;
}
.brand-icon {
    width: 38px; height: 38px;
    background: linear-gradient(135deg, #1a56db, #3b82f6);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
}
.brand-title {
    font-size: 18px;
    font-weight: 700;
    color: #111827;
    letter-spacing: -0.3px;
}
.brand-title span { color: #1a56db; }
.brand-sub {
    font-size: 12px;
    color: #6B7280;
    margin-bottom: 1.2rem;
    line-height: 1.4;
    padding-left: 2px;
}

/* ── New chat button ── */
[data-testid="stSidebar"] .stButton:first-of-type > button {
    background: transparent !important;
    border: 1.5px solid #1a56db !important;
    color: #1a56db !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    padding: 8px 16px !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton:first-of-type > button:hover {
    background: #1a56db !important;
    color: #fff !important;
}

/* ── Sidebar section labels ── */
.sidebar-section {
    font-size: 11px;
    font-weight: 600;
    color: #9CA3AF;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 1.2rem 0 0.5rem;
}

/* ── Conversation list buttons ── */
[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: none !important;
    color: #374151 !important;
    text-align: left !important;
    font-size: 13.5px !important;
    font-weight: 400 !important;
    padding: 7px 10px !important;
    border-radius: 7px !important;
    transition: background 0.15s !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #EEF2FF !important;
    color: #1a56db !important;
}

/* ── Active conversation ── */
.active-conv button {
    background: #EEF2FF !important;
    color: #1a56db !important;
    font-weight: 500 !important;
}

/* ── Upload area ── */
[data-testid="stFileUploader"] {
    background: #F8FAFF !important;
    border: 1.5px dashed #C7D3F5 !important;
    border-radius: 10px !important;
    padding: 8px !important;
}
[data-testid="stFileUploader"] label { display: none; }

/* ── Build index button ── */
[data-testid="stSidebar"] .stButton[data-testid="build-btn"] > button,
[data-testid="stSidebar"] .element-container:last-child .stButton > button {
    background: linear-gradient(135deg, #1a56db, #3b82f6) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    box-shadow: 0 2px 8px rgba(26,86,219,0.25) !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .element-container:last-child .stButton > button:hover {
    box-shadow: 0 4px 16px rgba(26,86,219,0.35) !important;
    transform: translateY(-1px) !important;
}

/* ── Main content area ── */
.main .block-container {
    background: #FFFFFF;
    border-radius: 16px;
    margin: 1rem 1rem 0 0.5rem;
    padding: 2rem 2.5rem !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 8px 32px rgba(26,86,219,0.05);
    min-height: calc(100vh - 2rem);
}

/* ── Chat title ── */
.chat-title {
    font-size: 22px;
    font-weight: 700;
    color: #111827;
    margin-bottom: 1.5rem;
    padding-bottom: 0.8rem;
    border-bottom: 1px solid #F3F4F6;
    letter-spacing: -0.4px;
}

/* ── User messages — right-aligned blue bubble ── */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]),
.stChatMessage[data-role="user"] {
    flex-direction: row-reverse !important;
    background: transparent !important;
    border: none !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) .stChatMessageContent,
.stChatMessage[data-role="user"] .stChatMessageContent {
    background: linear-gradient(135deg, #1a56db, #3b82f6) !important;
    color: #ffffff !important;
    border-radius: 18px 18px 4px 18px !important;
    padding: 12px 18px !important;
    max-width: 70% !important;
    margin-left: auto !important;
    box-shadow: 0 2px 8px rgba(26,86,219,0.2) !important;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) p {
    color: #ffffff !important;
}

/* ── Assistant messages — left white card ── */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) .stChatMessageContent,
.stChatMessage[data-role="assistant"] .stChatMessageContent {
    background: #F8FAFF !important;
    border: 1px solid #E5E9F5 !important;
    border-radius: 18px 18px 18px 4px !important;
    padding: 14px 20px !important;
    max-width: 80% !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    color: #1F2937 !important;
}

/* ── Avatar icons ── */
[data-testid="stChatMessageAvatarUser"] {
    background: #E0E7FF !important;
    border-radius: 50% !important;
}
[data-testid="stChatMessageAvatarAssistant"] {
    background: linear-gradient(135deg, #1a56db, #3b82f6) !important;
    border-radius: 50% !important;
}

/* ── Source pill tags ── */
.source-tag {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: #EEF2FF;
    border: 1px solid #C7D3F5;
    color: #1a56db;
    font-size: 12px;
    font-weight: 500;
    padding: 4px 10px;
    border-radius: 20px;
    margin: 3px 4px 3px 0;
    font-family: 'DM Mono', monospace;
}
.sources-label {
    font-size: 12px;
    font-weight: 600;
    color: #6B7280;
    margin: 8px 0 4px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}

/* ── Chat input bar ── */
[data-testid="stChatInput"] {
    border: 1.5px solid #E5E9F5 !important;
    border-radius: 12px !important;
    background: #F8FAFF !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: #1a56db !important;
    box-shadow: 0 0 0 3px rgba(26,86,219,0.1) !important;
}
[data-testid="stChatInput"] textarea {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 14px !important;
    color: #111827 !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #9CA3AF !important;
}
[data-testid="stChatInputSubmitButton"] button {
    background: linear-gradient(135deg, #1a56db, #3b82f6) !important;
    border-radius: 8px !important;
    border: none !important;
}

/* ── Welcome empty state ── */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    color: #9CA3AF;
}
.empty-icon {
    font-size: 48px;
    margin-bottom: 1rem;
}
.empty-state h3 {
    font-size: 20px;
    font-weight: 600;
    color: #374151;
    margin-bottom: 0.5rem;
}
.empty-state p {
    font-size: 14px;
    color: #6B7280;
    max-width: 360px;
    margin: 0 auto 1.5rem;
    line-height: 1.6;
}
.feature-chips {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    justify-content: center;
    margin-top: 1rem;
}
.feature-chip {
    background: #EEF2FF;
    border: 1px solid #C7D3F5;
    color: #1a56db;
    font-size: 12px;
    font-weight: 500;
    padding: 5px 12px;
    border-radius: 20px;
}

/* ── Status indicator ── */
.status-dot {
    display: inline-block;
    width: 7px; height: 7px;
    border-radius: 50%;
    background: #10B981;
    margin-right: 5px;
    vertical-align: middle;
}
.status-dot.off { background: #D1D5DB; }
.index-status {
    font-size: 12px;
    color: #6B7280;
    margin-top: 6px;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* ── Divider ── */
hr {
    border: none !important;
    border-top: 1px solid #F3F4F6 !important;
    margin: 1rem 0 !important;
}

/* ── Spinner ── */
.stSpinner > div { border-top-color: #1a56db !important; }

/* ── Success / warning ── */
.stSuccess { border-radius: 8px !important; }
.stWarning { border-radius: 8px !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #E5E9F5; border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: #C7D3F5; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# One-time setup
# ---------------------------------------------------------------------------
db.init_db()
if "index_loaded" not in st.session_state:
    st.session_state.index_loaded = rag.load_index_from_disk()

# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
with st.sidebar:

    # Brand header
    st.markdown("""
    <div class="brand-header">
        <div class="brand-icon">🧠</div>
        <div class="brand-title">DocuMind <span>AI</span></div>
    </div>
    <div class="brand-sub">Ask questions about your uploaded documents</div>
    """, unsafe_allow_html=True)

    # New chat
    if st.button("＋  New chat", use_container_width=True):
        new_id = db.create_conversation()
        st.session_state.conversation_id = new_id
        st.rerun()

    # Recent chats
    conversations = db.list_conversations()
    if conversations:
        st.markdown('<div class="sidebar-section">Recent chats</div>', unsafe_allow_html=True)
        for conv in conversations:
            col1, col2 = st.columns([5, 1])
            is_active = st.session_state.get("conversation_id") == conv["id"]
            label = ("● " if is_active else "") + conv["title"]
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

    # Upload section
    st.markdown('<div class="sidebar-section">Upload documents</div>', unsafe_allow_html=True)
    uploaded_files = st.file_uploader(
        "PDF or HTML files",
        type=["pdf", "html", "htm"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if st.button("⚡  Build index", use_container_width=True, type="primary"):
        if not uploaded_files:
            st.warning("Upload at least one file first.")
        else:
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
            st.success(f"✅ Ready — {result['total_chunks']} chunks · {result['total_files']} file(s)")

            # Auto-collapse sidebar after building index
            st.session_state.close_sidebar = True

    # Index status
    status = rag.get_status()
    if status["loaded"]:
        st.markdown(
            f'<div class="index-status"><span class="status-dot"></span>'
            f'{status["total_chunks"]} chunks · {len(status["files"])} file(s) indexed</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="index-status"><span class="status-dot off"></span>No index — upload files above</div>',
            unsafe_allow_html=True,
        )

# Auto-collapse sidebar after index build
if st.session_state.get("close_sidebar"):
    st.session_state.close_sidebar = False
    st.markdown("""
        <script>
            const btn = window.parent.document.querySelector('[data-testid="collapsedControl"]');
            if (btn) btn.click();
        </script>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# MAIN CHAT AREA
# ---------------------------------------------------------------------------
status = rag.get_status()

if "conversation_id" not in st.session_state:
    conversations = db.list_conversations()
    if conversations:
        st.session_state.conversation_id = conversations[0]["id"]
    else:
        new_id = db.create_conversation()
        st.session_state.conversation_id = new_id

conversation_id = st.session_state.conversation_id
messages = db.load_messages(conversation_id)

# Chat title
conv_list = db.list_conversations()
current_conv = next((c for c in conv_list if c["id"] == conversation_id), None)
title = current_conv["title"] if current_conv else "New chat"
st.markdown(f'<div class="chat-title">{title}</div>', unsafe_allow_html=True)

# Empty state — shown when no messages yet
if not messages:
    st.markdown("""
    <div class="empty-state">
        <div class="empty-icon">🧠</div>
        <h3>How can I help you today?</h3>
        <p>Upload your university documents in the sidebar, build the index, then ask me anything about them.</p>
        <div class="feature-chips">
            <span class="feature-chip">📄 PDF & HTML support</span>
            <span class="feature-chip">🔍 Semantic search</span>
            <span class="feature-chip">📍 Source citations</span>
            <span class="feature-chip">⚡ Streaming answers</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Render all past messages
for msg in messages:
    with st.chat_message(msg["role"], avatar="🧠" if msg["role"] == "assistant" else "👤"):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input(
    "Ask a question about your documents..." if status["loaded"] else "Upload and index documents to start chatting...",
    disabled=not status["loaded"],
)

if user_input:
    # Show user message
    with st.chat_message("user", avatar="👤"):
        st.markdown(user_input)

    db.save_message(conversation_id, "user", user_input)

    # Auto-title on first message
    if db.get_message_count(conversation_id) == 1:
        db.auto_title(conversation_id, user_input)

    # Retrieve chunks + build history
    retrieved_chunks = rag.search(user_input, top_k=5)
    history = db.load_messages(conversation_id)
    history_for_api = history[:-1]

    # Stream the response
    with st.chat_message("assistant", avatar="🧠"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            for chunk in ask_claude_streaming(user_input, retrieved_chunks, history_for_api):
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        except Exception as e:
            full_response = f"⚠️ Something went wrong: {str(e)}"
            response_placeholder.error(full_response)

        # Source citations as pill tags
        if retrieved_chunks:
            sources_html = '<div class="sources-label">Sources</div><div>'
            seen = set()
            for src in retrieved_chunks:
                key = f"{src['file_name']} · Page {src['page_number']}"
                if key not in seen:
                    seen.add(key)
                    sources_html += f'<span class="source-tag">📄 {src["file_name"]} · p.{src["page_number"]}</span>'
            sources_html += "</div>"
            st.markdown(sources_html, unsafe_allow_html=True)

    db.save_message(conversation_id, "assistant", full_response)
    st.rerun()