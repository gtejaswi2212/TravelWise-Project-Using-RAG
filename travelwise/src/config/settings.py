from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    root_dir: Path = Path(__file__).resolve().parents[3]
    data_dir: Path = root_dir / "data"
    raw_data_dir: Path = data_dir / "raw"
    processed_data_dir: Path = data_dir / "processed"
    docs_dir: Path = root_dir / "Docs"
    vector_index_dir: Path = Path(os.getenv("VECTOR_INDEX_DIR", data_dir / "vectorstore" / "nyc_faiss"))

    # Model + tool keys
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    tavily_api_key: str | None = os.getenv("TAVILY_API_KEY")
    langchain_api_key: str | None = os.getenv("LANGCHAIN_API_KEY")

    # Optional LangSmith tracing config
    langchain_tracing_v2: str = os.getenv("LANGCHAIN_TRACING_V2", "false")
    langchain_project: str = os.getenv("LANGCHAIN_PROJECT", "TravelWise")

    llm_model: str = os.getenv("CHAT_MODEL", os.getenv("TRAVELWISE_MODEL", "gemini-1.5-flash"))
    embedding_model: str = os.getenv(
        "EMBEDDING_MODEL", os.getenv("TRAVELWISE_EMBEDDING_MODEL", "models/embedding-001")
    )
    embedding_backend: str = os.getenv("EMBEDDING_BACKEND", "gemini").lower()

    top_k: int = int(os.getenv("TOP_K", "4"))
    chunk_size: int = int(os.getenv("CHUNK_SIZE", "700"))
    chunk_overlap: int = int(os.getenv("CHUNK_OVERLAP", "120"))
    use_web_fallback: bool = os.getenv("USE_WEB_FALLBACK", "true").lower() == "true"
    include_pdf_docs: bool = os.getenv("INCLUDE_PDF_DOCS", "false").lower() == "true"


settings = Settings()


def validate_settings(cfg: Settings) -> list[str]:
    """Return human-readable startup warnings instead of hard-failing."""
    warnings: list[str] = []

    if cfg.embedding_backend == "gemini" and not cfg.gemini_api_key:
        warnings.append(
            "EMBEDDING_BACKEND=gemini but GEMINI_API_KEY is missing. Falling back to local hash embeddings."
        )

    if not cfg.gemini_api_key:
        warnings.append("GEMINI_API_KEY is missing. App will run in grounded fallback generation mode.")

    if cfg.use_web_fallback and not cfg.tavily_api_key:
        warnings.append(
            "USE_WEB_FALLBACK=true but TAVILY_API_KEY is missing. Web tool disabled, routing will fallback to vector retrieval."
        )

    if not cfg.raw_data_dir.exists():
        warnings.append(f"Raw data directory not found: {cfg.raw_data_dir}")

    if cfg.top_k <= 0:
        warnings.append("TOP_K must be > 0. Using value <= 0 can break retrieval behavior.")

    return warnings
