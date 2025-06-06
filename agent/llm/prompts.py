def build_initial_prompt(user_query: str, tools_json: str) -> str:
    return (
        "You are an AI assistant that answers only in English.\n"
        "You can call external tools using tool calls.\n\n"
        "**Important rules:**\n"
        "- Do NOT guess.\n"
        "- If the question relates to a tool, you MUST call it first.\n"
        "- Only respond using a tool call when needed:\n"
        '  <tool_call>{"name": "...", "arguments": {...}}</tool_call>\n\n'
        "<tools>\n"
        f"{tools_json}\n"
        "</tools>\n\n"
        f"User: {user_query}\n\n"
        "🚨 If the question relates to a tool, respond immediately with a tool call.\n"
        "Do NOT ask the user to clarify. Pick the best-fitting tool and use it directly.\n"
    )

def build_followup_prompt(user_query: str, tool_outputs: list[tuple[str, str]]) -> str:
    tool_sections = "\n\n".join(
        f"--- Result from {tool_name} ---\n{output}" for tool_name, output in tool_outputs
    )

    seen_urls = []
    for name, output in tool_outputs:
        if name == "fetch_ollama_metadata":
            try:
                model_line = next(line for line in output.splitlines() if line.startswith("Model:"))
                model_name = model_line.split(":", 1)[1].strip()
                seen_urls.append(model_name)
            except Exception:
                pass

    seen_note = (
        "\n\n⚠️ Already fetched metadata for: " + ", ".join(seen_urls) +
        "\n➡️ Do NOT fetch metadata for these again. Pick a different model URL from the list."
        if seen_urls else ""
    )

    return (
        f"The user asked: {user_query}\n\n"
        "You have already used these tools:\n\n"
        f"{tool_sections}\n\n"
        "If needed, call another tool to gather more information.\n"
        "Only give a final answer if you're confident it's complete."
        f"{seen_note}\n\n"
        "📌 Use this format for tool calls:\n"
        "<tool_call>\n"
        '{"name": "TOOL_NAME", "arguments": {"param1": "value1", ...}}\n'
        "</tool_call>\n\n"
        "Do NOT use natural language or code-style syntax like fetch_tool(...).\n"
        "To call 'fetch_ollama_metadata', you must pass a full `url` string from ollama.com.\n"
    )


def build_final_prompt(user_query: str, tool_outputs: list[tuple[str, str]]) -> str:
    tool_sections = "\n\n".join(
        f"--- Result from {tool_name} ---\n{output}" for tool_name, output in tool_outputs
    )

    return (
        f"The user asked: {user_query}\n\n"
        "You gathered the following information from tool calls:\n\n"
        f"{tool_sections}\n\n"
        "✅ Now give a final, complete answer.\n"
        "🚫 Do NOT call any more tools.\n"
        "Respond in natural language with your full answer.\n"
    )