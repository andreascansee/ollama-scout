from tools.tool_base import Tool
import requests
from bs4 import BeautifulSoup

class SearchOllamaModels(Tool):
    @property
    def name(self) -> str:
        return "search_ollama_models"

    def run(self, args: dict) -> str:
        query = args.get("query", "")
        search_url = f"https://ollama.com/search?q={query}"
        try:
            response = requests.get(search_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return f"[ERROR] Failed to fetch results: {e}"

        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        seen = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            if href.startswith('/library/') and href.count('/') == 2:
                name = href.split('/')[-1]
                if name in seen:
                    continue
                seen.add(name)
                full_url = f"https://ollama.com{href}"
                results.append({'name': name, 'url': full_url})
            if len(results) >= 5:
                break

        if not results:
            return "No results found."

        return "\n".join(f"{r['name']} → {r['url']}" for r in results)