from pathlib import Path

from travelwise.src.agents.router import QueryRouter
from travelwise.src.chunking.chunker import chunk_documents
from travelwise.src.embeddings.providers import HashEmbeddings
from travelwise.src.loaders.nyc_loader import load_nyc_documents
from travelwise.src.retrieval.retriever import RetrievalService
from travelwise.src.vectorstore.index_manager import build_faiss_index


def test_router_routes_realtime_queries_to_web():
    router = QueryRouter(web_enabled=True)
    assert router.route("What events are happening tonight in NYC?") == "web"


def test_local_retrieval_smoke(tmp_path: Path):
    docs = load_nyc_documents(Path("data/raw"), docs_dir=None)
    chunks = chunk_documents(docs, chunk_size=500, chunk_overlap=50)

    vectorstore = build_faiss_index(chunks, HashEmbeddings(), tmp_path / "index")
    service = RetrievalService(vectorstore=vectorstore, top_k=3)
    context, sources, debug = service.retrieve("best pizza spots in brooklyn")

    assert context
    assert len(sources) > 0
    assert len(debug) > 0
