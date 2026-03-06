from __future__ import annotations

import json
from pathlib import Path

import fitz
from langchain_core.documents import Document


def _load_pdf_documents(pdf_path: Path) -> list[Document]:
    pages: list[Document] = []
    with fitz.open(pdf_path) as doc:
        for i, page in enumerate(doc):
            text = page.get_text().strip()
            if not text:
                continue
            pages.append(
                Document(
                    page_content=text,
                    metadata={
                        "source": str(pdf_path.name),
                        "source_type": "pdf",
                        "page": i + 1,
                        "title": pdf_path.stem,
                    },
                )
            )
    return pages


def load_nyc_documents(raw_data_dir: Path, docs_dir: Path | None = None) -> list[Document]:
    docs: list[Document] = []

    knowledge_file = raw_data_dir / "nyc_knowledge.json"
    if knowledge_file.exists():
        rows = json.loads(knowledge_file.read_text(encoding="utf-8"))
        for row in rows:
            docs.append(
                Document(
                    page_content=row["content"],
                    metadata={
                        "source": row.get("source", "nyc_knowledge.json"),
                        "source_type": row.get("source_type", "local_dataset"),
                        "title": row.get("title", "NYC Knowledge"),
                        "category": row.get("category", "general"),
                        "neighborhood": row.get("neighborhood", "NYC"),
                        "tags": row.get("tags", []),
                    },
                )
            )

    if docs_dir and docs_dir.exists():
        for pdf in sorted(docs_dir.glob("*.pdf")):
            docs.extend(_load_pdf_documents(pdf))

    return docs
