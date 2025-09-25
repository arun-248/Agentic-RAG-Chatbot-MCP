# app.py
"""
Streamlit UI for the Agentic RAG Chatbot (MCP-based).
This file is the entry point for the demo application.

Key Features:
- Allows users to upload multi-format documents (PDF, DOCX, PPTX, CSV, TXT/MD).
- Provides a text input box for natural language questions.
- Displays chatbot answers + retrieved context.
- Shows MCP (Model Context Protocol) message log in sidebar and UI for debugging/demo purposes.
"""

import streamlit as st
import tempfile
import os
from coordinator_agent import handle_uploads_and_query
from mcp import send_mcp_message

# -------------------------------
# Streamlit Page Configuration
# -------------------------------
st.set_page_config(page_title="Agentic RAG Chatbot (MCP)", layout="wide")
st.title("Agentic RAG Chatbot — Demo (MCP visible)")

# -------------------------------
# Session State Initialization
# -------------------------------
if "mcp_log" not in st.session_state:
    st.session_state["mcp_log"] = []  # stores MCP messages for UI display

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []  # keeps conversation turns: {"user":..., "assistant":...}

def add_mcp_to_state(msg: dict):
    """Helper to append MCP message to Streamlit session state."""
    st.session_state["mcp_log"].append(msg)

# -------------------------------
# Sidebar: MCP Logs
# -------------------------------
st.sidebar.header("MCP Message Log")
st.sidebar.write("MCP messages are also printed in the terminal. "
                 "This panel shows the last messages for convenience in demos.")

# -------------------------------
# File Upload Section
# -------------------------------
uploaded_files = st.file_uploader(
    "Upload documents (PDF, PPTX, CSV, DOCX, TXT/MD)", 
    accept_multiple_files=True
)

saved_paths = []
if uploaded_files:
    for f in uploaded_files:
        # Save uploaded file to a temporary path (needed for ingestion agent)
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(f.name)[1])
        tmp.write(f.getbuffer())
        tmp.flush()
        tmp.close()
        saved_paths.append(tmp.name)

    st.success(f"✅ Saved {len(saved_paths)} files for ingestion.")

# -------------------------------
# User Query Section
# -------------------------------
query = st.text_input("Ask a question about the uploaded documents:")

col1, col2 = st.columns([3, 1])

# -------------------------------
# Column 1: Main Chat Interaction
# -------------------------------
with col1:
    if st.button("Ask") and query:
        # 1. Log MCP message (UI -> CoordinatorAgent)
        m = send_mcp_message(
            sender="UI",
            receiver="CoordinatorAgent",
            type="USER_QUERY",
            payload={"query": query}
        )
        add_mcp_to_state(m)

        # 2. Orchestrate flow (IngestionAgent → RetrievalAgent → LLMResponseAgent)
        resp = handle_uploads_and_query(saved_paths, query)

        # 3. Store in conversation history
        st.session_state["chat_history"].append({
            "user": query,
            "assistant": resp.get("answer", "")
        })

        # 4. Display final chatbot answer
        st.subheader("Answer")
        st.write(resp.get("answer", ""))

# -------------------------------
# Column 2: Conversation + Logs
# -------------------------------
with col2:
    st.subheader("Conversation (latest turns)")
    for turn in reversed(st.session_state["chat_history"][-20:]):
        st.markdown(f"**You:** {turn['user']}")
        st.markdown(f"**Assistant:** {turn['assistant']}")

    st.write("---")
    st.subheader("MCP Log (last 10 messages)")
    # Note: MCP messages are also printed to terminal for easier PPT/video capture
    for msg in st.session_state["mcp_log"][-10:]:
        st.json(msg)

# -------------------------------
# Sidebar Footer Note
# -------------------------------
st.sidebar.write("💡 Tip: Run this app from a terminal so MCP messages printed to console "
                 "are visible for your PPT/video demo.")
