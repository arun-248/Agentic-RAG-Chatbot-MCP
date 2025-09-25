# retrieval_agent.py
"""
Retrieval Agent

This module handles embedding + semantic search.
It builds a FAISS index over document chunks and retrieves relevant context.

Flow:
1. Index chunks (from IngestionAgent)
2. Encode query → retrieve top_k chunks
3. Send MCP message with retrieved context to LLMResponseAgent
"""

import logging
from typing import List, Dict
from mcp import send_mcp_message

from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

logging.basicConfig(level=logging.INFO)

EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBED_DIM = 384


class RetrievalAgent:
    def __init__(self):
        # Load embedding model
        self.model = SentenceTransformer(EMBED_MODEL)
        self.index = None
        self.metadatas: List[Dict] = []
        self.texts: List[str] = []

    def build_index(self, chunks: List[Dict]):
        """
        Build or extend FAISS index with new chunks.
        """
        texts = [c["text"] for c in chunks]
        vectors = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        vectors = np.array(vectors).astype("float32")
        faiss.normalize_L2(vectors)

        if self.index is None:
            self.index = faiss.IndexFlatIP(EMBED_DIM)

        self.index.add(vectors)
        self.texts.extend(texts)
        for c in chunks:
            self.metadatas.append(c.get("meta", {}))

        logging.info("RetrievalAgent: index size now %d", self.index.ntotal)

    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve top-k most relevant chunks for a query.
        """
        if self.index is None or self.index.ntotal == 0:
            return []

        q_vec = self.model.encode([query], convert_to_numpy=True)
        q_vec = np.array(q_vec).astype("float32")
        faiss.normalize_L2(q_vec)

        D, I = self.index.search(q_vec, top_k)
        results = []
        for score, idx in zip(D[0], I[0]):
            if idx < 0:
                continue
            results.append({
                "score": float(score),
                "meta": self.metadatas[idx],
                "text": self.texts[idx]
            })
        return results


# -------------------------------
# Global default agent (singleton style)
# -------------------------------
_default_agent = RetrievalAgent()


def index_chunks(chunks: List[Dict]):
    """
    Wrapper: index new chunks.
    """
    _default_agent.build_index(chunks)


def handle_query(query: str, top_k: int = 5) -> List[Dict]:
    """
    Wrapper: retrieve and send MCP message.
    """
    top = _default_agent.retrieve(query, top_k=top_k)
    send_mcp_message(
        sender="RetrievalAgent",
        receiver="LLMResponseAgent",
        type="RETRIEVAL_RESULT",
        payload={"retrieved_context": top, "query": query}
    )
    return top
