import json
import os
from tools.fetch import FetchOllamaMetadata

OUTPUT_DIR = "ollama_docs"

def save_metadata(model_name: str, content: dict, output_dir: str = OUTPUT_DIR):
    os.makedirs(output_dir, exist_ok=True)
    filename = os.path.join(output_dir, f"{model_name}.json")
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(content, f, indent=2, ensure_ascii=False)
    print(f"✅ Metadata saved to: {filename}")

def main():
    tool = FetchOllamaMetadata()
    url = input("🌐 Enter Ollama model URL: ").strip()
    model_name = url.rstrip("/").split("/")[-1]

    print(f"🔎 Fetching metadata for: {model_name}")
    output = tool.run({"url": url})

    if "error" in output:
        print(output["error"])
    else:
        print(f"📤 Tool output:\n{json.dumps(output, indent=2)}")
        save_metadata(model_name, output)

if __name__ == "__main__":
    main()
