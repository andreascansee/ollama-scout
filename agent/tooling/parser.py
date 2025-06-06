import json
import re

def extract_tool_call(text: str) -> dict | None:
    """
    Attempts to extract a tool call from model output.

    The function supports three formats:
    1. Structured <tool_call>{...}</tool_call> wrapping valid JSON.
    2. Inline JSON containing "name" and "arguments".
    3. Fallback match for just a {"query": "..."} string (assumes 'search_ollama_models').

    Returns:
        dict: A dictionary with 'name' and 'arguments' if a tool call is detected,
              otherwise None.
    """

    # 1. Preferred format: <tool_call>{...}</tool_call>
    match = re.search(r"<tool_call>\s*(\{.*?\})\s*</tool_call>", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))  # parse the JSON inside the tag
        except json.JSONDecodeError:
            return None  # Invalid JSON, ignore

    # 2. Fallback: inline JSON like {"name": "tool", "arguments": {...}}
    match = re.search(
        r'(\{.*?"name"\s*:\s*".+?",\s*"arguments"\s*:\s*\{.*?\}\s*\})',
        text,
        re.DOTALL
    )
    if match:
        try:
            return json.loads(match.group(1))  # direct JSON object
        except json.JSONDecodeError:
            return None

    # 3. Lowest fallback: just a single query field (assume search tool)
    match = re.search(r'\{.*?"query"\s*:\s*"(.*?)".*?\}', text)
    if match:
        return {
            "name": "search_ollama_models",
            "arguments": {"query": match.group(1)}
        }

    # Nothing matched
    return None