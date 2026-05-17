# DocuMind AI

**DocuMind AI** is a Retrieval-Augmented Generation (RAG) based intelligent document question-answering system. It allows users to upload PDF and HTML documents, ask natural language questions, and receive context-aware answers generated from the uploaded documents with source citations.

The system is designed as an AI-powered document assistant for academic, enterprise, and policy-based documents where users need quick and accurate answers from large document collections.

---

## Project Title

**DocuMind AI: A Retrieval-Augmented Generation (RAG) Based Intelligent Document Question Answering System Using Large Language Models**

---

## Research Question

**How effectively can Retrieval-Augmented Generation (RAG) improve the accuracy and contextual relevance of answers generated from unstructured documents?**

---

## Problem Statement

Many organisations and students rely on large PDF documents, policy files, course specifications, handbooks, and internal knowledge documents. Searching these documents manually is time-consuming and inefficient. Traditional keyword search often fails to understand the meaning of user questions or retrieve the most relevant information.

DocuMind AI addresses this problem by using semantic search and large language models to retrieve relevant document sections and generate clear answers based only on the uploaded content.

---

## Proposed Solution

DocuMind AI uses a RAG pipeline to combine document retrieval with AI-generated responses.

The system works as follows:

1. Users upload PDF or HTML documents.
2. The system extracts text from the uploaded files.
3. The extracted text is split into smaller chunks.
4. Each chunk is converted into embeddings using a Sentence Transformer model.
5. The embeddings are stored in a FAISS vector index.
6. When a user asks a question, the system retrieves the most relevant chunks.
7. The retrieved context is sent to a Large Language Model through the Groq API.
8. The AI generates an answer using only the retrieved document context.
9. The answer is displayed with source document names and page numbers.

---

## Key Features

- Upload and process PDF and HTML documents
- Ask questions in natural language
- Semantic document search using embeddings
- FAISS-based vector retrieval
- LLM-powered answer generation using Groq API
- Real-time streaming responses
- Source citation with document name and page number
- Persistent chat history using SQLite
- Multiple conversation support
- Streamlit-based user interface
- Deployable to Streamlit Cloud

---

## System Architecture

```text
User
 ↓
Streamlit Frontend
 ↓
Document Upload
 ↓
Text Extraction
 ↓
Text Chunking
 ↓
Sentence Transformer Embeddings
 ↓
FAISS Vector Database
 ↓
User Question
 ↓
Semantic Retrieval
 ↓
Groq LLM API
 ↓
Generated Answer
 ↓
Answer + Source Citations
