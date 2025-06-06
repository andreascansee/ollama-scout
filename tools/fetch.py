from tools.tool_base import Tool
import requests
from bs4 import BeautifulSoup

class FetchOllamaMetadata(Tool):
    @property
    def name(self) -> str:
        return "fetch_ollama_metadata"

    def run(self, args: dict) -> dict:
        url = args.get("url", "")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            return {"error": f"[ERROR] Failed to fetch URL: {e}"}

        soup = BeautifulSoup(response.text, "html.parser")
        base_name = url.rstrip("/").split("/")[-1]

        downloads = updated = None
        for span in soup.find_all("span"):
            text = span.get_text(strip=True).lower()
            if text == "downloads":
                prev = span.find_previous_sibling("span")
                if prev:
                    downloads = prev.get_text(strip=True)
            elif text == "updated":
                next = span.find_next_sibling("span")
                if next:
                    updated = next.get_text(strip=True)

        desc_tag = soup.find("span", id="summary-content")
        description = desc_tag.get_text(strip=True) if desc_tag else None

        readme_div = soup.find("div", id="readme")
        readme_paragraphs = []
        if readme_div:
            for p in readme_div.find_all("p"):
                text = p.get_text(strip=True)
                if text:
                    readme_paragraphs.append(text)

        models = []
        for sec in soup.find_all("section"):
            heading = sec.find("h2")
            if heading and heading.get_text(strip=True) == "Models":
                for row in sec.find_all("div", class_="sm:grid"):
                    name_tag = row.find("a", class_="text-sm")
                    model_name = name_tag.get_text(strip=True) if name_tag else None
                    col_tags = row.find_all("p", class_="col-span-2")
                    size = col_tags[0].get_text(strip=True) if len(col_tags) > 0 else None
                    context = col_tags[1].get_text(strip=True) if len(col_tags) > 1 else None
                    input_type = col_tags[2].get_text(strip=True) if len(col_tags) > 2 else None

                    if model_name:
                        models.append({
                            "name": model_name,
                            "size": size,
                            "context": context,
                            "input": input_type
                        })

        return {
            "model": base_name,
            "downloads": downloads or "n/a",
            "updated": updated or "n/a",
            "description": description or "n/a",
            "variants": models,
            "readme_paragraphs": readme_paragraphs
        }
