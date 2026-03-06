from __future__ import annotations

from tavily import TavilyClient

from travelwise.src.utils.types import RetrievedSource


class WebSearchService:
    def __init__(self, api_key: str | None) -> None:
        self.client = TavilyClient(api_key=api_key) if api_key else None

    def enabled(self) -> bool:
        return self.client is not None

    def search(self, query: str, max_results: int = 4) -> tuple[str, list[RetrievedSource], list[dict]]:
        if not self.client:
            return "", [], []

        response = self.client.search(query=query, max_results=max_results)
        rows = response.get("results", [])

        lines: list[str] = []
        sources: list[RetrievedSource] = []
        debug_rows: list[dict] = []

        for i, row in enumerate(rows, start=1):
            title = row.get("title") or row.get("url", "web")
            content = row.get("content", "").strip()
            url = row.get("url", "")
            lines.append(f"[{i}] {title}: {content}")

            sources.append(
                RetrievedSource(
                    source=title,
                    snippet=content[:380],
                    metadata={"url": url, "source_type": "web"},
                )
            )
            debug_rows.append({"rank": i, "title": title, "url": url, "snippet": content[:500]})

        return "\n\n".join(lines), sources, debug_rows
