from __future__ import annotations

import hashlib
from typing import Iterable

import numpy as np
import requests
from langchain_core.embeddings import Embeddings


class GeminiEmbeddings(Embeddings):
    def __init__(self, api_key: str, model: str = "models/gemini-embedding-001") -> None:
        self.api_key = api_key
        self.model = model
        self.endpoint = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-embedding-001:embedContent"
        )

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_query(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        payload = {
            "model": self.model,
            "content": {"parts": [{"text": text[:8000]}]},
        }
        response = requests.post(
            f"{self.endpoint}?key={self.api_key}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        return data["embedding"]["values"]


class HashEmbeddings(Embeddings):
    """Deterministic local fallback for offline demos/tests."""

    def __init__(self, dim: int = 256) -> None:
        self.dim = dim

    def _embed(self, text: str) -> list[float]:
        vec = np.zeros(self.dim, dtype=np.float32)
        tokens = [tok.strip(".,!?;:()[]{}\"'").lower() for tok in text.split()]
        for tok in tokens:
            if not tok:
                continue
            h = hashlib.sha256(tok.encode("utf-8", errors="ignore")).digest()
            idx = int.from_bytes(h[:4], "big", signed=False) % self.dim
            sign = -1.0 if h[4] % 2 else 1.0
            vec[idx] += sign
        vec = vec / (np.linalg.norm(vec) + 1e-12)
        return vec.tolist()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)


def embedding_from_config(backend: str, gemini_api_key: str | None, model: str) -> Embeddings:
    if backend == "gemini" and gemini_api_key:
        return GeminiEmbeddings(api_key=gemini_api_key, model=model)
    return HashEmbeddings()