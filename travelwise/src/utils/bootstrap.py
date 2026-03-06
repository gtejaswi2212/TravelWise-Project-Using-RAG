from __future__ import annotations

from pathlib import Path

from travelwise.src.agents.router import QueryRouter
from travelwise.src.agents.travel_agent import TravelWiseAgent
from travelwise.src.chunking.chunker import chunk_documents
from travelwise.src.embeddings.providers import embedding_from_config
from travelwise.src.generation.generator import ResponseGenerator
from travelwise.src.loaders.nyc_loader import load_nyc_documents
from travelwise.src.retrieval.retriever import RetrievalService
from travelwise.src.retrieval.web_search import WebSearchService
from travelwise.src.utils.config import Settings
from travelwise.src.vectorstore.index_manager import (
    build_faiss_index,
    load_faiss_index,
    write_chunk_debug,
)


def build_index(settings: Settings) -> dict:
    docs_dir = settings.docs_dir if settings.include_pdf_docs else None
    docs = load_nyc_documents(settings.raw_data_dir, docs_dir)
    if not docs:
        raise ValueError("No documents found to index.")

    chunks = chunk_documents(
        docs,
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    embeddings = embedding_from_config(
        backend=settings.embedding_backend,
        gemini_api_key=settings.gemini_api_key,
        model=settings.embedding_model,
    )
    build_faiss_index(chunks, embeddings, settings.vector_index_dir)
    write_chunk_debug(chunks, settings.processed_data_dir / "chunks_debug.jsonl")

    return {
        "documents": len(docs),
        "chunks": len(chunks),
        "index_dir": str(settings.vector_index_dir),
        "chunk_debug": str(settings.processed_data_dir / "chunks_debug.jsonl"),
    }


def ensure_index_exists(index_dir: Path) -> bool:
    return (index_dir / "index.faiss").exists() and (index_dir / "index.pkl").exists()


def create_agent(settings: Settings) -> TravelWiseAgent:
    embeddings = embedding_from_config(
        backend=settings.embedding_backend,
        gemini_api_key=settings.gemini_api_key,
        model=settings.embedding_model,
    )

    if not ensure_index_exists(settings.vector_index_dir):
        build_index(settings)

    vectorstore = load_faiss_index(settings.vector_index_dir, embeddings)
    retrieval = RetrievalService(vectorstore=vectorstore, top_k=settings.top_k)
    generator = ResponseGenerator(api_key=settings.gemini_api_key, model=settings.llm_model)
    router = QueryRouter(web_enabled=settings.use_web_fallback)
    web = WebSearchService(api_key=settings.tavily_api_key) if settings.use_web_fallback else None

    return TravelWiseAgent(retriever=retrieval, generator=generator, router=router, web_search=web)
