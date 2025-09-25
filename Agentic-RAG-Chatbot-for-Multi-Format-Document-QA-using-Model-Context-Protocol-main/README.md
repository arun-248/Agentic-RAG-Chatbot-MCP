# Agentic RAG Chatbot (Multi-Format Document QA with MCP)

An **agent-based Retrieval-Augmented Generation (RAG) chatbot** that answers user questions from uploaded documents (PDF, PPTX, CSV, DOCX, TXT/Markdown).  

The system is built with an **agentic architecture** and implements **Model Context Protocol (MCP)** for structured communication between agents.

---

## 🚀 Features

- ✅ **Multi-format Document Upload & Parsing**  
  (PDF, PPTX, DOCX, CSV, TXT/MD)

- 🤖 **Agentic Architecture (3 Agents)**  
  - **IngestionAgent** → Parses and preprocesses documents  
  - **RetrievalAgent** → Performs embedding + semantic retrieval  
  - **LLMResponseAgent** → Builds final query, calls LLM (or generates stub answers if no key is set)  

- 🧩 **Model Context Protocol (MCP)**  
  All agents exchange structured JSON messages:  

  ```json
  {
    "sender": "RetrievalAgent",
    "receiver": "LLMResponseAgent",
    "type": "RETRIEVAL_RESULT",
    "trace_id": "rag-1234",
    "payload": {
      "retrieved_context": ["Revenue up 18% in 2024", "NPS improved to 71"],
      "query": "What are the KPIs?"
    }
  }
📚 **Vector Store + Embeddings**

- Embeddings: `all-MiniLM-L6-v2` (HuggingFace)  
- Vector DB: **FAISS** for similarity search  

💬 **Interactive Chatbot UI** (Streamlit)  

- 📁 Upload multi-format documents  
- 🔁 Ask multi-turn questions  
- 🧾 Get answers with source context + MCP logs  

---

## 🧰 Tech Stack

- **Language** → Python  
- **UI** → Streamlit  
- **Embeddings** → SentenceTransformers (`all-MiniLM-L6-v2`)  
- **Vector Store** → FAISS  
- **Protocol Layer** → Custom MCP (in-memory)  
- **LLM** → Groq (live) OR regex-based stub mode (free demo mode)  

---

## 🔧 Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/<your-username>/Agentic-RAG-Chatbot-MCP.git
cd Agentic-RAG-Chatbot-MCP
### 2. Create Virtual Environment (recommended)
```bash
python -m venv .venv
source .venv/bin/activate   # Linux / Mac
.venv\Scripts\activate      # Windows
### 3. Install Requirements
```bash
pip install -r requirements.txt
### 4. Set Up Environment Variables

Create a `.env` file in the project root.  

If you have a Groq API key, add it:

```bash
GROQ_API_KEY=your-groq-api-key
⚠️ If no key is set → chatbot works in stub mode (regex-based answers only).
### 5. Run the App

```bash
streamlit run app.py
## 📸 Deliverables for Coding Test

- **GitHub Repo** → Code + README  
- **PPT Slides** →  
  - Agentic architecture (3 agents + MCP message flow)  
  - System workflow diagram  
  - Tech stack  
  - UI screenshots  
  - Challenges & Future scope  

- **Demo Video (optional)** →  
  Show app, explain flow, quick code walkthrough  

---

✅ This version is now **100% README-friendly** — no mixing text/code, everything is Markdown.
