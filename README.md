# TravelWise: Adaptive RAG Travel Assistant for NYC

TravelWise is a portfolio-grade Applied AI project that demonstrates **adaptive RAG** for travel planning in New York City. It routes queries between a local vector knowledge base and live web search (Tavily), then returns grounded responses with source attribution.

## Problem Statement
Most travel chatbots either hallucinate or become stale. TravelWise solves this by combining:
- **local retrieval** for stable NYC guidance (itineraries, neighborhoods, museum/food planning)
- **web retrieval** for dynamic information (events, weather, closures, ticket/hours updates)
- **grounded generation** with transparent sources and debug metadata

## Why This Project Matters (AI Engineer Positioning)
This project highlights practical AI engineering skills recruiters look for:
- adaptive retrieval and tool routing
- modular RAG system design
- environment-driven configuration
- source-grounded responses
- evaluation and observability mindset
- productized Streamlit demo UX

## Key Features
- Adaptive router with explicit modes:
  - `VECTOR_ONLY`
  - `WEB_ONLY`
  - `VECTOR_THEN_WEB_FALLBACK`
- FAISS vector retrieval over curated NYC knowledge
- Tavily web fallback for fresh/dynamic questions
- Retrieval confidence heuristic for fallback decisions
- Source attribution (local + web URLs)
- Streamlit chat app with route indicators and debug panel
- Environment checks (`python run.py doctor`)

## Architecture Overview
High-level flow:
1. User asks a travel question in Streamlit.
2. Router decides retrieval mode.
3. System uses vector retrieval and/or Tavily search.
4. Context builder aggregates evidence with source metadata.
5. LLM generator returns grounded answer with practical formatting.

Architecture docs:
- [Architecture write-up](Docs/architecture.md)
- [Mermaid source](diagrams/travelwise_architecture.mmd)
- [Architecture PNG](Docs/architecture.png)

## Tech Stack
- **App/UI**: Streamlit
- **API**: Flask
- **RAG**: LangChain + FAISS
- **Embeddings/LLM**: Gemini (with local fallback mode)
- **Web tool**: Tavily
- **Data**: JSON + optional PDF ingestion
- **Testing**: Pytest

## Repository Structure
```text
TravelWise-Project-Using-RAG/
├── app.py
├── run.py
├── README.md
├── requirements.txt
├── .env.example
├── demo/
│   ├── screenshots/
│   └── demo_script.md
├── docs/
│   ├── architecture.md
│   ├── architecture.png
│   └── prompts.md
├── diagrams/
│   └── travelwise_architecture.mmd
├── data/
│   ├── raw/
│   │   └── nyc_knowledge.json
│   ├── processed/
│   └── vectorstore/
├── notebooks/
├── tests/
│   └── test_rag_smoke.py
└── travelwise/
    ├── app/
    │   ├── api/server.py
    │   └── ui/streamlit_app.py
    └── src/
        ├── config/settings.py
        ├── ingestion/
        ├── retrieval/
        ├── routing/
        ├── llm/
        ├── tools/
        ├── chains/
        ├── evaluation/
        └── utils/
```

## Adaptive Routing Logic
- **`WEB_ONLY`**: dynamic intent detected (`today`, `tonight`, `weather`, `news`, `hours`, `price`, `events`) and Tavily is configured.
- **`VECTOR_ONLY`**: static intent or web tool unavailable.
- **`VECTOR_THEN_WEB_FALLBACK`**: vector retrieval first; if confidence is low and Tavily is available, web context is appended.

## Setup
### 1. Install
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configure environment
```bash
cp .env.example .env
```

Required/important variables:
- `GEMINI_API_KEY=` recommended for best generation/embedding quality
- `TAVILY_API_KEY=` optional but needed for live web fallback
- `EMBEDDING_MODEL=` default `models/gemini-embedding-001`
- `CHAT_MODEL=` default `gemini-1.5-flash`
- `LANGCHAIN_TRACING_V2=` optional (`true`/`false`)
- `LANGCHAIN_PROJECT=` default `TravelWise`

Tavily key setup:
1. Create account at [Tavily](https://app.tavily.com/home)
2. Copy API key
3. Add to `.env` as `TAVILY_API_KEY=...`

### 3. Build index
```bash
python run.py build-index
```

### 4. Run app
```bash
streamlit run travelwise/app/ui/streamlit_app.py
```

## Additional Commands
```bash
python run.py doctor          # config validation and startup warnings
python run.py eval            # sample query evaluation pass
python run.py api             # Flask API mode
pytest -q                     # smoke tests
```

## Data Ingestion
- Seed data: `data/raw/nyc_knowledge.json`
- Optional PDFs: `Docs/*.pdf` (enable with `INCLUDE_PDF_DOCS=true`)
- Chunk debug output: `data/processed/chunks_debug.jsonl`

## Sample Queries
- Plan me a 1-day food tour in Manhattan
- What are the top museums near Central Park?
- Suggest a budget-friendly 2-day NYC itinerary
- What are the best pizza spots in Brooklyn?
- Things to do near Times Square in the evening
- What events are happening tonight near Times Square?

## Screenshots
Capture and place under `demo/screenshots/`:
- `home.png` (hero + sidebar status)
- `vector_answer.png` (itinerary with local citations)
- `adaptive_or_web.png` (dynamic query showing mode/path)
- `debug_panel.png` (retrieval confidence + route metadata)

## Evaluation and Observability
- `run.py eval` tests representative queries and retrieval behavior.
- UI debug panel exposes:
  - routing mode
  - execution path
  - retrieval confidence
  - source list
- `run.py doctor` surfaces missing key/config warnings.

## Limitations
- Without `GEMINI_API_KEY`, responses run in fallback mode.
- Without `TAVILY_API_KEY`, adaptive web routing degrades to vector-only fallback.
- Current confidence metric is heuristic; can be upgraded with learned rerankers.

## Extensibility Roadmap
- Add hybrid retrieval (BM25 + dense)
- Add reranker for higher precision top-k context
- Add structured JSON output mode for itinerary UI rendering
- Add automated regression/eval suite with answer quality checks
- Expand to multi-city support via pluggable datasets
