# 🎓 AI-Powered Research Assistant

> **An intelligent academic companion that combines local knowledge with real-time external research.**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)
![Grok](https://img.shields.io/badge/AI-Grok-black.svg)

## 🌟 Overview

The **AI-Powered Research Assistant** is a sophisticated tool designed to help researchers navigate complex academic landscapes. Unlike traditional search engines, it doesn't just find papers; it **understands** your research intent.

Powered by **Grok AI**, the system orchestrates a suite of tools to:
1.  **Search** your local vector database for relevant papers.
2.  **Expand** the search to external sources (arXiv, PubMed, Semantic Scholar) via the **Model Context Protocol (MCP)** if local data is insufficient.
3.  **Detect** research gaps and missing connections in the literature.
4.  **Synthesize** comprehensive answers with inline citations.

All of this is delivered through a modern, responsive **Glassmorphism UI** with real-time streaming responses.

---

## ✨ Key Features

### 🧠 Intelligent Orchestration
*   **Intent Analysis**: Automatically determines if you need a broad search, specific fact-checking, or gap analysis.
*   **Smart Routing**: Dynamically selects the best tools for the job (e.g., routing medical queries to PubMed).
*   **Sufficiency Checking**: Evaluates if found papers are enough to answer the query; if not, it triggers an external search.

### 🔍 Hybrid Search Engine
*   **Local Vector Search**: Ultra-fast similarity search using `pgvector` and Sentence Transformers.
*   **External MCP Integration**: Real-time access to:
    *   📚 **arXiv** (CS, Physics, Math)
    *   🏥 **PubMed** (Biomedical)
    *   🎓 **Semantic Scholar** (General Science)

### ⚡ Real-Time Streaming
*   **Instant Feedback**: See exactly what the agent is doing ("Analyzing intent...", "Searching database...").
*   **Token-by-Token Generation**: Answers stream in naturally, reducing perceived latency.
*   **Concurrent Execution**: Papers and gaps appear as soon as they are found, while the AI writes the answer.

### 💡 Advanced Analysis
*   **Gap Detection**: Proactively identifies areas where research is missing or contradictory.
*   **Citation Management**: Automatically formats inline citations `[Author, Year]` and links to sources.

---

## 🛠️ Tech Stack

### Frontend
*   **Framework**: React 18 (Vite)
*   **Language**: TypeScript
*   **Styling**: Tailwind CSS (Glassmorphism design)
*   **State Management**: React Hooks

### Backend
*   **Framework**: Flask (Python)
*   **Async**: `asyncio` for concurrent tool execution
*   **API**: REST + Server-Sent Events (SSE) for streaming

### AI & Data
*   **LLM**: Grok (xAI) via API
*   **Embeddings**: HuggingFace Sentence Transformers
*   **Database**: PostgreSQL (with `pgvector` extension)
*   **Caching**: Redis (Conversation memory & session management)

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.8+
*   Node.js 16+
*   Redis Server
*   PostgreSQL (with `pgvector`)

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/research-assistant.git
cd research-assistant
```

### 2. Backend Setup
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory:
```env
GROK_API_KEY=your_grok_api_key
DATABASE_URL=postgresql://user:password@localhost:5432/research_db
REDIS_URL=redis://localhost:6379/0
```

### 3. Frontend Setup
```bash
cd ../
npm install
```

### 4. Running the Application

**Start Redis:**
```bash
redis-server
```

**Start Backend:**
```bash
cd backend
python3 app.py
# Server runs on http://localhost:5000
```

**Start Frontend:**
```bash
# In root directory
npm run dev
# App runs on http://localhost:5174
```

---

## 📖 Usage Guide

1.  **Open the UI**: Navigate to `http://localhost:5174`.
2.  **Ask a Question**: Type a query like *"What are the limitations of transformer architectures?"*.
3.  **Watch it Work**:
    *   The status bar will update: `Analyzing intent...` -> `Searching...`.
    *   **Papers** will appear in the "Evidence" panel on the right.
    *   **Gaps** (if found) will appear in the "Gaps" panel.
    *   The **Answer** will stream in the main chat window.
4.  **Explore**: Click on papers to view abstracts or external links.

---

## 🔌 API Documentation

### `POST /api/chat/stream`
Streams the response for a user query.

**Request:**
```json
{
  "query": "What is deep learning?",
  "session_id": "optional-uuid"
}
```

**Response (Streamed NDJSON):**
```json
{"type": "status", "content": "Searching..."}
{"type": "tool_data", "data": [...]}
{"type": "token", "content": "Deep"}
{"type": "token", "content": " learning"}
...
{"type": "done"}
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
