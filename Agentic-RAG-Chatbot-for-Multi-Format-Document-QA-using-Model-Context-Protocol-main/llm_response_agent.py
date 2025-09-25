# llm_response_agent.py
"""
LLM Response Agent

This module builds prompts from retrieved context and generates final answers.

Modes:
- Stub Mode (no GROQ_API_KEY): Extracts values (Revenue, CAC, NPS, etc.) with regex for demo.
- Live Mode (with API key): Calls Groq API (or other LLM endpoint).

Always sends FINAL_RESPONSE MCP message back to the UI.
"""

import os
import logging
from typing import Dict, List
from mcp import send_mcp_message
import requests
import re

logging.basicConfig(level=logging.INFO)

# Environment variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = os.getenv("GROQ_API_URL", "https://api.groq.com/v1/llm")  # Developer note: replace with actual endpoint


# -------------------------------
# Stub Answer Extraction
# -------------------------------
def extract_stub_answers(text: str) -> str:
    """
    Extracts key metrics from retrieved text for stub mode.
    Useful for coding test demos without paid LLM API access.
    """
    # Revenue 2023
    match_2023 = re.search(r"\$[0-9.]+\s*billion.*2023", text)
    if match_2023:
        value = re.search(r"\$[0-9.]+\s*billion", match_2023.group())
        if value:
            return f"(Stub Answer) Revenue in 2023 was {value.group()}"

    # Revenue 2024
    match_2024 = re.search(r"\$[0-9.]+\s*billion.*2024", text)
    if match_2024:
        value = re.search(r"\$[0-9.]+\s*billion", match_2024.group())
        if value:
            return f"(Stub Answer) Revenue in 2024 was {value.group()}"

    # CAC
    match_cac = re.search(r"CAC.*?\$[0-9]+", text, re.IGNORECASE)
    if match_cac:
        value = re.search(r"\$[0-9]+", match_cac.group())
        if value:
            return f"(Stub Answer) Customer Acquisition Cost was {value.group()}"

    # NPS
    match_nps = re.search(r"NPS.*?(\d{2})", text, re.IGNORECASE)
    if match_nps:
        return f"(Stub Answer) Net Promoter Score was {match_nps.group(1)}"

    # Retention
    match_ret = re.search(r"Retention rate was (\d+)%", text, re.IGNORECASE)
    if match_ret:
        return f"(Stub Answer) Retention rate was {match_ret.group(1)}%"

    # Churn
    match_churn = re.search(r"churn rate (decreased to|was) (\d+)%", text, re.IGNORECASE)
    if match_churn:
        return f"(Stub Answer) Churn rate was {match_churn.group(2)}%"

    # Employee satisfaction
    match_emp = re.search(r"Employee satisfaction.*?(\d+)%", text, re.IGNORECASE)
    if match_emp:
        return f"(Stub Answer) Employee satisfaction score was {match_emp.group(1)}%"

    # Carbon footprint
    match_carbon = re.search(r"carbon footprint.*?(\d+)%", text, re.IGNORECASE)
    if match_carbon:
        return f"(Stub Answer) Carbon footprint reduced by {match_carbon.group(1)}%"

    # Fallback: just preview
    short_preview = text[:400].replace("\n", " ")
    return f"(Stub Answer) {short_preview}"


# -------------------------------
# LLM API Call
# -------------------------------
def call_llm(prompt: str, retrieved: List[Dict], max_tokens: int = 512) -> Dict:
    """
    Call the LLM API (Groq or stub).
    """
    if not GROQ_API_KEY:
        logging.warning("GROQ_API_KEY not set; using local stub LLM.")
        if retrieved:
            text = " ".join([r.get("text", "") for r in retrieved[:3]])
            answer = extract_stub_answers(text)
            return {"answer": answer, "raw": None}
        else:
            return {"answer": "(Stub Answer) No relevant context found.", "raw": None}

    # With API key → call real endpoint
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"}
    payload = {"prompt": prompt, "max_tokens": max_tokens}

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        answer = data.get("output", data.get("answer", ""))
        return {"answer": answer, "raw": data}
    except Exception as e:
        logging.exception("LLM call failed: %s", e)
        return {"answer": f"[LLM error] {str(e)}", "raw": None}


# -------------------------------
# Prompt Formatting
# -------------------------------
def format_prompt(query: str, retrieved: List[Dict]) -> str:
    builder = []
    builder.append("You are a helpful assistant. Use only the context below to answer the question. If the answer is not present, say you don't know.")
    builder.append(f"\n### Query:\n{query}\n")
    builder.append("### Context (top chunks):\n")
    for i, r in enumerate(retrieved):
        meta = r.get("meta", {})
        builder.append(f"[Chunk {i}] source={meta.get('filename')} idx={meta.get('chunk_index')} score={r.get('score')}\n{r.get('text')}\n---\n")
    builder.append("\nProvide a concise answer, and list which chunk(s) were used as sources (by filename + chunk_index).")
    return "\n".join(builder)


# -------------------------------
# Answer Query
# -------------------------------
def answer_query(query: str, retrieved: List[Dict]) -> Dict:
    """
    Generate a final answer using retrieved context.
    """
    prompt = format_prompt(query, retrieved)
    logging.info("LLMResponseAgent: sending prompt (len=%d chars)", len(prompt))

    llm_resp = call_llm(prompt, retrieved)
    answer = llm_resp.get("answer", "")

    # Send MCP back to UI
    send_mcp_message(
        sender="LLMResponseAgent",
        receiver="UI",
        type="FINAL_RESPONSE",
        payload={"query": query, "answer": answer, "retrieved": retrieved, "llm_raw": llm_resp.get("raw")}
    )

    return {"answer": answer, "retrieved": retrieved}
