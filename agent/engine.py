from agent.model import query_model
from agent.prompts import build_initial_prompt, build_followup_prompt, build_final_prompt
from agent.tool_parser import extract_tool_call
from agent.tool_registry import call_tool
import json

def is_duplicate_tool_call(name: str, arguments: dict, previous_calls: list[tuple[str, dict]]) -> bool:
    """
    Checks whether a tool call with the same name and arguments has already been made.
    Prevents repeated identical calls that waste steps and API quota.
    """
    return any(prev_name == name and prev_args == arguments for prev_name, prev_args in previous_calls)


def run_agent_loop(user_query: str, tools_json: str) -> str:
    """
    Multi-step agent loop to answer a question using tools as needed.
    
    Behavior:
    - Starts with initial prompt
    - Sends up to 5 tool-related steps (model + tool call + new prompt)
    - Avoids duplicate tool calls with same arguments
    - At the end, sends a final prompt to generate a natural-language answer

    Args:
        user_query: The original question asked by the user
        tools_json: Tool definitions (as JSON string) passed to the model

    Returns:
        A final answer string from the model, after using any tools needed
    """
    tool_outputs = []  # [(tool_name, output_text), ...]
    tool_calls = []    # [(tool_name, arguments_dict), ...]
    max_steps = 4

    current_prompt = build_initial_prompt(user_query, tools_json)

    for step in range(max_steps):
        # Debug: show current prompt
        print(f"\n🔄 Step {step + 1} / {max_steps}")
        print("🧠 Sending prompt to model:\n")
        print(current_prompt)
        print("\n" + "=" * 60 + "\n")

        response = query_model(current_prompt)
        tool_call = extract_tool_call(response)

        if not tool_call:
            print("\n⚠️ No tool_call extracted. Raw model response:\n")
            print(response)
            return response  # Stop if model didn't return a valid tool call

        # Debug: print extracted tool call
        print("\n🛠 Tool call extracted:")
        print(json.dumps(tool_call, indent=2))

        tool_name = tool_call["name"]
        arguments = tool_call["arguments"]

        # Skip if this exact tool call was already made
        if is_duplicate_tool_call(tool_name, arguments, tool_calls):
            print(f"\n⚠️ Skipping duplicate tool call: {tool_name} with same arguments.")
            continue

        # Call the tool and handle errors
        try:
            tool_result = call_tool(tool_call)
        except Exception as e:
            print(f"\n❌ Tool '{tool_name}' failed: {e}")
            return f"[ERROR] Tool failed: {e}"

        # Debug: show tool output
        print(f"\n✅ Result from tool '{tool_name}':\n{tool_result}")

        tool_outputs.append((tool_name, tool_result))
        tool_calls.append((tool_name, arguments))

        # Build next prompt with updated tool outputs
        current_prompt = build_followup_prompt(user_query, tool_outputs)

    # After tool loop: ask model to give final answer
    final_prompt = build_final_prompt(user_query, tool_outputs)

    # Debug: show final prompt
    print("\n🧠 Final prompt to model for full answer:\n")
    print(final_prompt)
    print("\n" + "=" * 60 + "\n")

    final_response = query_model(final_prompt)
    return final_response