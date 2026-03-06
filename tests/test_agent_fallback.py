from pathlib import Path

from travelwise.src.agents.router import QueryRouter
from travelwise.src.agents.travel_agent import TravelWiseAgent
from travelwise.src.embeddings.providers import HashEmbeddings
from travelwise.src.generation.generator import ResponseGenerator
from travelwise.src.loaders.nyc_loader import load_nyc_documents
from travelwise.src.retrieval.retriever import RetrievalService
from travelwise.src.vectorstore.index_manager import build_faiss_index
from travelwise.src.chunking.chunker import chunk_documents


def test_web_only_query_falls_back_to_vector_when_web_unavailable(tmp_path):
    docs = load_nyc_documents(Path("data/raw"), docs_dir=None)
    chunks = chunk_documents(docs, chunk_size=500, chunk_overlap=50)
    vs = build_faiss_index(chunks, HashEmbeddings(), tmp_path / "index")

    agent = TravelWiseAgent(
        retriever=RetrievalService(vs, top_k=3),
        generator=ResponseGenerator(api_key=None, model="gemini-1.5-flash"),
        router=QueryRouter(web_enabled=True),
        web_search=None,
    )

    result = agent.answer("What events are happening tonight near Times Square?")
    assert result.route == "vector"
    assert "web_fallback_reason" in result.debug
