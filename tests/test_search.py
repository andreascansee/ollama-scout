import os
import json
from tools.search import SearchOllamaModels

OUTPUT_DIR = "ollama_models"

def save_model_list(query: str, model_list: list, output_dir: str = OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{query.lower()}.json")

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(model_list, f, ensure_ascii=False, indent=2)

    print(f"✅ Results saved to: {filename}")

def main():
    tool = SearchOllamaModels()
    query = input("🔍 What model would you like to search for? ").strip()
    output = tool.run({"query": query})

    print(f"📤 Tool output:\n{output}")
    save_model_list(query, output)

if __name__ == "__main__":
    main()
