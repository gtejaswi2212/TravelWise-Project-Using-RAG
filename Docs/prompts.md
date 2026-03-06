# Prompt Strategy

## System behavior prompt
The generator prompt enforces:
- grounded answers using only retrieved context
- explicit uncertainty when context is limited
- itinerary formatting with `Morning`, `Afternoon`, `Evening`
- practical transit/budget notes where relevant
- source-aware output

## Routing policy
The router classifies queries by intent:
- Live/dynamic intents (`today`, `tonight`, `hours`, `weather`, `news`, `price`) -> `WEB_ONLY` when Tavily is configured
- Static travel guidance -> `VECTOR_THEN_WEB_FALLBACK`

## Fallback strategy
If vector confidence is low and Tavily is configured, the chain appends web context and returns a blended grounded answer (`vector+web`).

## Example test prompts
- Plan me a 1-day food tour in Manhattan
- What are the top museums near Central Park?
- What events are happening tonight in NYC?
- Are there any subway disruptions today?
