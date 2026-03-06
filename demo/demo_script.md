# 60-90s Recruiter Demo Script

## 1) Open (10s)
"This is TravelWise, an adaptive RAG assistant for NYC. It routes between a local vector knowledge base and live Tavily web search based on query type and retrieval confidence."

## 2) Static query (20s)
Ask: `Plan me a 1-day food tour in Manhattan`
- Point out: route mode is `VECTOR_THEN_WEB_FALLBACK`
- Show: local sources and grounded itinerary format

## 3) Dynamic query (20s)
Ask: `What events are happening tonight near Times Square?`
- Point out: route mode and whether web tool is used (or vector fallback if Tavily key missing)
- Show: source attribution and debug panel

## 4) Engineering quality (20s)
- Show project structure (`travelwise/src/...`)
- Mention config-driven setup (`.env`, `run.py doctor`)
- Mention evaluability (`python run.py eval`, `pytest -q`)

## 5) Close (10s)
"The key idea is adaptive retrieval: best source selection per query, grounded responses, and observability for debugging quality."

## Suggested demo questions
- Suggest a budget-friendly 2-day NYC itinerary
- What are the best pizza spots in Brooklyn?
- Things to do near Times Square in the evening
- What is the weather in NYC today? (web-oriented)

## Screenshot capture checklist
1. Home screen with title and sidebar status
2. A vector-grounded itinerary answer with local citations
3. A dynamic query showing route mode and debug panel
