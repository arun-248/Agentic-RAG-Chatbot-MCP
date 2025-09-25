# coordinator_agent.py
"""
Coordinator Agent

This module orchestrates the flow of the Agentic RAG Chatbot using the MCP (Model Context Protocol).
It acts as the "conductor" that connects the individual agents:

1. IngestionAgent → parses and chunks uploaded documents
2. RetrievalAgent → indexes chunks and retrieves relevant context
3. LLMResponseAgent → generates the final answer using retrieved context

The CoordinatorAgent ensures that:
- All MCP messages are sent between agents.
- The pipeline runs in the correct order (Ingest → Index → Retrieve → Answer).
"""

from typing import List, Dict
from mcp import send_mcp_message
from ingestion_agent import process_document
from retrieval_agent import index_chunks, handle_query
from llm_response_agent import answer_query


def handle_uploads_and_query(file_paths: List[str], query: str) -> Dict:
    """
    Orchestrate the end-to-end pipeline for a user query.

    Args:
        file_paths (List[str]): List of file paths uploaded by the user.
        query (str): Natural language query from the user.

    Returns:
        Dict: Final response object with answer + retrieved context.
    """

    # -------------------------------
    # Step 1: Ingest all files
    # -------------------------------
    all_chunks = []
    for p in file_paths:
        # Each document is parsed and split into chunks by IngestionAgent
        chunks = process_document(p, filename=p)
        all_chunks.extend(chunks)

    # Send MCP message: Coordinator → RetrievalAgent (index building)
    send_mcp_message(
        sender="CoordinatorAgent",
        receiver="RetrievalAgent",
        type="BUILD_INDEX",
        payload={"n_chunks": len(all_chunks)}
    )

    # -------------------------------
    # Step 2: Index chunks
    # -------------------------------
    if all_chunks:
        index_chunks(all_chunks)

    # -------------------------------
    # Step 3: Retrieve relevant context
    # -------------------------------
    retrieved = handle_query(query, top_k=5)

    # -------------------------------
    # Step 4: Generate LLM answer
    # -------------------------------
    response = answer_query(query, retrieved)

    return response
