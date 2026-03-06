from __future__ import annotations

import json
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings


def build_faiss_index(documents: list[Document], embeddings: Embeddings, index_dir: Path) -> FAISS:
    index_dir.mkdir(parents=True, exist_ok=True)
    vectorstore = FAISS.from_documents(documents, embeddings)
    vectorstore.save_local(str(index_dir), index_name="index")
    return vectorstore


def load_faiss_index(index_dir: Path, embeddings: Embeddings) -> FAISS:
    return FAISS.load_local(
        str(index_dir),
        embeddings,
        allow_dangerous_deserialization=True,
        index_name="index",
    )


def write_chunk_debug(documents: list[Document], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for i, doc in enumerate(documents, start=1):
            row = {
                "chunk_id": i,
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
