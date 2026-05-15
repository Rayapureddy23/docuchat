# DocuMind AI — ChatGPT-like document chatbot

A RAG-powered chatbot that answers questions about your uploaded PDFs and HTML pages,
built with Streamlit + Claude API + FAISS.

## Project structure

```
docuchat/
├── app.py            ← Main Streamlit app (the UI)
├── llm.py            ← Claude API brain + streaming (Steps 1 & 2)
├── rag.py            ← Document ingestion + FAISS search (Step 3)
├── database.py       ← SQLite chat history (Step 4)
├── requirements.txt  ← All dependencies
├── .gitignore
└── .streamlit/
    ├── config.toml   ← App theme and server settings
    └── secrets.toml  ← Your API key (local only, never commit)
```

---

## Step 1 — Get your API key

Sign up at https://console.anthropic.com and create an API key.

---

## Step 2 — Set up locally

```bash
# Clone or download this folder, then:
cd docuchat

# Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Add your API key to the secrets file
# Edit .streamlit/secrets.toml and replace the placeholder key
```

---

## Step 3 — Run the app

```bash
streamlit run app.py
```

Your browser will open at http://localhost:8501

---

## Step 4 — Use the app

1. In the sidebar, upload your PDF or HTML files
2. Click **Build index** — this processes and embeds all documents
3. Type a question in the chat input at the bottom
4. The app will retrieve relevant chunks and stream Claude's answer in real time
5. All conversations are saved automatically — restart the app and your history is still there

---

## Step 5 — Deploy to Streamlit Cloud (free)

1. Push this folder to a **GitHub repository** (the `.gitignore` will keep your key safe)
2. Go to https://share.streamlit.io
3. Click **New app** → select your repo → set main file to `app.py`
4. Click **Advanced settings** → **Secrets** → paste this:
   ```toml
   ANTHROPIC_API_KEY = "sk-ant-your-actual-key"
   ```
5. Click **Deploy** — your app is live in ~2 minutes

---

## What each file replaces from your notebook

| Old notebook code                        | New file        |
|------------------------------------------|-----------------|
| `bart-large-cnn` + messy prompt          | `llm.py`        |
| `all_documents`, `chunk_data`, FAISS     | `rag.py`        |
| `chat_history = []` (in-memory)          | `database.py`   |
| `ipywidgets` textarea + button           | `app.py`        |
| `from google.colab import files`         | `st.file_uploader` in `app.py` |
| No persistence (lost on restart)         | SQLite + `faiss.write_index()` |