from tools.tool_base import Tool
from tools.search import SearchOllamaModels
from tools.fetch import FetchOllamaMetadata

# Instantiate and register all available tools
REGISTERED_TOOLS: dict[str, Tool] = {
    tool.name: tool for tool in [
        SearchOllamaModels(),
        FetchOllamaMetadata(),
        # More Tool instances can go here later
    ]
}

def call_tool(tool_call: dict) -> str:
    """
    Executes the appropriate tool function based on the tool_call input.

    Args:
        tool_call (dict): {
            "name": str - tool name,
            "arguments": dict - arguments for the tool
        }

    Returns:
        str: The tool output, formatted for prompting
    """
    name = tool_call.get("name")
    args = tool_call.get("arguments", {})

    tool = REGISTERED_TOOLS.get(name)
    if not tool:
        return f"[ERROR] Unknown tool: {name}"

    try:
        return tool.run(args)
    except Exception as e:
        return f"[ERROR] Tool '{name}' failed: {e}"
