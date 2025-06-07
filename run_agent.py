import json
from agent.engine import run_agent_loop

def main():
    # Load tool definitions and reformat them as pretty JSON string for model input
    with open("configs/ollama_tools.json") as f:
        tools_json = json.dumps(json.load(f), indent=2)

    # Prompt the user to enter their question
    user_query = input("❓ Your question: ").strip()

    # Run the multi-step agent loop with the user question and tools
    response = run_agent_loop(user_query, tools_json)

    # Print the final answer returned by the agent
    print("📦 Final answer:\n", response)

# Ensure this script runs only when executed directly (not on import)
if __name__ == "__main__":
    main()