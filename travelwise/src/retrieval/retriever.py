from __future__ import annotations

import re

from langchain_community.vectorstores import FAISS

from travelwise.src.utils.types import RetrievedSource


class RetrievalService:
    def __init__(self, vectorstore: FAISS, top_k: int = 4) -> None:
        self.vectorstore = vectorstore
        self.top_k = top_k

    def retrieve(self, query: str, k: int | None = None) -> tuple[str, list[RetrievedSource], list[dict]]:
        k = k or self.top_k
        docs_with_scores = self.vectorstore.similarity_search_with_score(query, k=max(k * 2, 8))
        query_terms = set(re.findall(r"[a-z0-9]+", query.lower()))
        query_terms = {t for t in query_terms if len(t) > 2}

        rescored = []
        for doc, score in docs_with_scores:
            text_terms = set(re.findall(r"[a-z0-9]+", doc.page_content.lower()))
            overlap = len(query_terms.intersection(text_terms))
            rescored.append((doc, float(score), overlap))

        rescored.sort(key=lambda row: (-row[2], row[1]))
        top = rescored[:k]

        sources: list[RetrievedSource] = []
        debug_rows: list[dict] = []
        snippets: list[str] = []

        for rank, (doc, score, overlap) in enumerate(top, start=1):
            source = doc.metadata.get("source", "unknown")
            title = doc.metadata.get("title", source)
            snippet = doc.page_content.strip()
            snippets.append(f"[{rank}] {snippet}")

            sources.append(
                RetrievedSource(
                    source=f"{title} ({source})",
                    snippet=snippet[:380],
                    score=float(score),
                    metadata=doc.metadata,
                )
            )

            debug_rows.append(
                {
                    "rank": rank,
                    "score": float(score),
                    "term_overlap": overlap,
                    "source": source,
                    "title": title,
                    "metadata": doc.metadata,
                    "snippet": snippet[:500],
                }
            )

        return "\n\n".join(snippets), sources, debug_rows

    @staticmethod
    def confidence(debug_rows: list[dict]) -> float:
        """Heuristic confidence score in [0,1] using lexical overlap from top results."""
        if not debug_rows:
            return 0.0
        top_overlap = debug_rows[0].get("term_overlap", 0)
        max_overlap = max(row.get("term_overlap", 0) for row in debug_rows[:3])
        # Saturating overlap curve for explainable confidence.
        raw = max(top_overlap, max_overlap) / 5.0
        return max(0.0, min(1.0, raw))
