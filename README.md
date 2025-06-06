# 🛰️ Ollama Scout

`ollama-scout` is a minimalist AI agent built from scratch that uses a local model (here, `qwen2.5:14b`) to explore and answer questions about other models in the Ollama library. 

It demonstrates how to extend LLM capabilities through simple tool-use, without relying on any complex frameworks.

## ✨ Motivation

I wanted to understand how tool-using agents work — so I built one as **purely** as possible: No LangChain, no plugins, no hidden abstractions. Just structured prompts, simple tool calls, and a local model.

To make the experiment meaningful, I picked a real-world weakness of LLMs: they often give **outdated or hallucinated** answers when asked about other LLMs.

**Example**:

Asking `qwen2.5:14b`:

> *What is DeepSeek?*

Returns something like:

> *As of my current knowledge, there isn't an official product or service called "DeepSeek" from Alibaba Cloud or any other major technology company.*

Which is **wrong** — DeepSeek is a real and actively developed family of open-source reasoning models.

> 🎯 So the goal became to give a local model **accurate, up-to-date knowledge** about a focused topic — in this case: **an older LLM that can reason about other, current LLMs (from the Ollama library)**.


## 🤖 What `ollama-scout` Does

Instead of relying on outdated or incomplete training data, `ollama-scout` augments a local model with live tooling:

- 🧭 **`search_ollama_models`** — queries the Ollama model library for relevant entries
- 📄 **`fetch_ollama_metadata`** — scrapes detailed metadata from a model's info page

The agent runs a multi-step reasoning loop:

1. Starts with a user question (e.g. *What is DeepSeek?*)
2. Chooses tools and arguments on its own — no hardcoded sequence
3. Builds a final answer from all collected information

> 🔍 This allows a relatively lightweight model—such as `qwen2.5:14b` with 14B parameters (~8 GB), in contrast to massive models like GPT-4, which may have up to 1T parameters—to perform grounded reasoning using up-to-date external sources.

## 🧾 Example Output

**User input**:  
> *What is DeepSeek?*

**Final answer**:
> *DeepSeek is a family of open-source reasoning models developed by the DeepSeek team, known for their strong performance in tasks such as mathematics, programming, and general logic...* 

Despite `qwen2.5:14b` having no built-in knowledge of DeepSeek, the agent was able to:
1. Run `search_ollama_models("deepseek")` to discover related models and URLs like `deepseek-r1 → https://ollama.com/library/deepseek-r1`
2. Use `fetch_ollama_metadata("https://ollama.com/library/deepseek-r1")` to retrieve and parse live information
3. Synthesize a coherent answer — entirely using local inference

> ⚙️ This demonstrates how small LLMs can be extended with real-time tools to provide current answers.

## 🛠 Tech Stack
- **Python 3.13**
  - Standard libraries, plus `BeautifulSoup` for lightweight HTML parsing (used by fetch tools)
- **Ollama (Local LLM Runtime)**
  - Install via [https://ollama.com/download](https://ollama.com/download) or your system's package manager
  - This project uses **Qwen2.5:14B**, a relatively small (≈8GB) but capable model with native support for function calling (tool use)
  - The model strikes a good balance between reasoning ability and runtime efficiency on consumer hardware

> ⚠️ You must download the model before use:
> ```bash
> ollama pull qwen2.5:14b
> ```

## 🗂️ Project Overview

```text
.
├── agent
│   ├── __init__.py
│   ├── controller.py
│   ├── llm
│   │   ├── model.py
│   │   └── prompts.py
│   └── tooling
│       ├── parser.py
│       └── runner.py
├── configs
│   └── ollama_tools.json
├── tests
│   ├── __init__.py
│   ├── test_fetch.py
│   └── test_search.py
├── tools
│   ├── __init__.py
│   ├── base.py
│   ├── fetch.py
│   └── search.py
├── README.md
├── requirements.txt
└── run_agent.py
```

### ▶️ Entry Point

- [`run_agent.py`](./run_agent.py) is the entry point of the application
- It loads tool definitions from [`ollama_tools.json`](./configs/ollama_tools.json) — which are used **only for prompt construction**, not for tool execution logic — and executes the main agent logic via the `run_agent_loop` function in [`controller.py`](./agent/controller.py)

### 🔁 Agent Control Loop 

- Defined in [`controller.py`](./agent/controller.py), the loop performs multi-step reasoning
- Prompts are sent to the model step by step, with a **maximum of 4 iterations**:
  - One **initial search**
  - Up to **three metadata fetches**
    > 🧠 The model can stop earlier if it decides it already has enough information to answer confidently. Not all steps are required
- Each model response is inspected for a `<tool_call>{...}</tool_call>` block
    - If no such block is found, the response is returned as-is and the loop ends
- If a tool call is found:
    - It is **parsed** using `extract_tool_call()` from [`parser.py`](./agent/tooling/parser.py)
    - Then **executed** using `dispatch_tool_call()` from [`runner.py`](./agent/tooling/runner.py)
    - **Duplicate tool calls** (same tool name + same arguments) are **skipped** to avoid redundancy
- The **result of each tool call** is fed back into the next prompt using `build_followup_prompt()` — so the model builds context with every step
- After the loop completes, a **final prompt** is sent to produce a natural-language answer from all collected tool results
   
### 🧰 Tools

- Tools are located in the [`tools/`](./tools/) directory
- Each tool is implemented as a class 
    - `SearchOllamaModels` in [`search.py`](./tools/search.py)
    - `FetchOllamaMetadata` in [`fetch.py`](./tools/fetch.py)
- All tools must inherit from the `Tool` base class defined in [`base.py`](./tools/base.py) and implement the following:
    - A `name` property used for dispatch
    - A `run()` method, which encapsulates the tool's logic
- This shared interface allows all tools to be executed generically via `tool.run(args)` without the controller needing to know their internal behavior

### 🪪 Tool Registry

- All tools must be registered in the `TOOL_REGISTRY` dictionary in [`runner.py`](./agent/tooling/runner.py)
- This file is responsible for:
    - Instantiating all available tool classes
    - Exposing the `dispatch_tool_call()` function, which dispatches tool calls by name and passes in arguments

### 🛎️ Prompt Templates

- Defined in [`prompts.py`](./agent/llm/prompts.py), these templates guide the agent's reasoning across three stages:
  - 🟢 **Initial prompt** — introduces the model to the user query and available tools
  - 🔄 **Follow-up prompts** — injected after each tool call and include all previous tool outputs
  - 🏁 **Final prompt** — instructs the model to compose a full, natural-language answer based on all collected information

### ⚙️ Model Config

- Model configuration is handled in [`model.py`](./agent/llm/model.py)
- By default, the agent queries a locally running Ollama server via HTTP using the `/api/generate` endpoint


## 🚀 Getting Started

1. First, set up a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run the agent:

```bash
python run_agent.py
```

## 🤹‍♂️ Experimentation 
You can easily extend or modify the agent's behavior:

- **Prompts**: Customize how the agent thinks by editing [`prompts.py`](./agent/llm/prompts.py).

- **Model**: Change the underlying model in [`model.py`](./agent/llm/model.py) by modifying the `MODEL_NAME` variable.

- **Add your own tools**:
  1. **Define**: Create a new Python class in `tools/` that inherits from `Tool` in [`base.py`](./tools/base.py). Put your logic in the `run` method.
  2. **Register**: Import and register the tool class in [`runner.py`](./agent/tooling/runner.py), so the controller can call it when needed.
  3. **Describe**: Add the new tool definition to [`ollama_tools.json`](./configs/ollama_tools.json), so the model is aware of it and can use it in tool calls.


## 🧪 Testing
You can test the individual tools independently of the agent loop:

```bash
python -m tests.test_search  # Runs the search tool, saves results to `ollama_models/`
python -m tests.test_fetch   # Runs the fetch tool, saves pages to `ollama_docs/`
```
> ℹ️ Using `-m` runs the module as a script, which ensures proper resolution of relative imports inside the tests package.

This is useful for debugging tool logic or collecting fresh data before a full agent run.

## ⚙️ Alternative: Use subprocess (no HTTP API)
If you want to avoid running the Ollama HTTP server, you can call the model directly via the command line using `subprocess`. Note: This avoids the HTTP API, but **Ollama still needs to be installed locally and accessible via CLI**.

To switch to this mode, replace the contents of [`model.py`](./agent/llm/model.py) with the following:

```python
import subprocess

def query_model(prompt: str) -> str:
    result = subprocess.run(
        ["ollama", "run", "qwen2.5:14b"],
        input=prompt,
        text=True,
        capture_output=True
    )
    return result.stdout.strip()
```