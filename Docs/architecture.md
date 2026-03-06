# TravelWise Architecture

## System overview
TravelWise uses adaptive routing to select the best knowledge source per query:
- `VECTOR_ONLY`: local retrieval only
- `WEB_ONLY`: Tavily for dynamic/live questions
- `VECTOR_THEN_WEB_FALLBACK`: local retrieval first, then Tavily when confidence is low

## Mermaid Diagram
```mermaid
flowchart LR
    U["User Query (Streamlit UI)"] --> R["Adaptive Router\n(VECTOR_ONLY | WEB_ONLY | VECTOR_THEN_WEB_FALLBACK)"]

    R -->|"vector path"| VR["Vector Retriever"]
    R -->|"web path"| WS["Tavily Web Search Tool"]

    KB["Local NYC Knowledge Base\n(JSON + Optional PDFs)"] --> ING["Ingestion + Chunking"] --> EMB["Embeddings"] --> VDB["FAISS Vector DB"] --> VR

    VR --> CB["Context Builder + Source Attribution"]
    WS --> CB

    CB --> LLM["LLM Response Generator\n(Gemini or fallback mode)"] --> UI["Streamlit Chat Response\n+ citations + debug panel"]

    CFG["Environment + Config Layer\n(.env, settings validation)"] -.-> R
    CFG -.-> WS
    CFG -.-> LLM
```

## Components
- Router: heuristic + retrieval confidence aware decision logic
- Retrieval: FAISS similarity search with lexical overlap rescoring
- Tooling: Tavily integration for dynamic questions and fallback
- Generation: grounded synthesis prompt with structured itinerary output style
- UI: Streamlit product demo with sources and debug observability
