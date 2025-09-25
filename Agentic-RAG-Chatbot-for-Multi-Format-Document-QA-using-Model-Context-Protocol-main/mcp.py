# mcp.py
"""
Model Context Protocol (MCP) Utilities

This module defines helper functions to create and send MCP messages.
MCP ensures structured communication between agents and the UI.
"""

import json
import uuid
import logging
from typing import Any, Dict

logging.basicConfig(level=logging.INFO)


def make_trace_id(prefix: str = "rag") -> str:
    """
    Generate a unique trace_id for correlating MCP messages.
    """
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def send_mcp_message(sender: str, receiver: str, type: str, payload: Dict[str, Any], trace_id: str = None) -> Dict[str, Any]:
    """
    Build and log an MCP message.

    Args:
        sender (str): Agent sending the message
        receiver (str): Target agent
        type (str): Message type (e.g., DOCUMENT_PARSED, RETRIEVAL_RESULT)
        payload (Dict): Actual data content
        trace_id (str, optional): For tracking. Auto-generated if None.

    Returns:
        Dict[str, Any]: Full MCP message object
    """
    if trace_id is None:
        trace_id = make_trace_id()

    message = {
        "sender": sender,
        "receiver": receiver,
        "type": type,
        "trace_id": trace_id,
        "payload": payload,
    }

    # Console print for demo purposes
    print("\n📩 MCP MESSAGE:")
    print(json.dumps(message, indent=2, ensure_ascii=False))

    logging.info("MCP message: %s -> %s : %s", sender, receiver, type)
    return message
