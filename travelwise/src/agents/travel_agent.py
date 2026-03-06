from __future__ import annotations

from travelwise.src.agents.router import QueryRouter
from travelwise.src.routing.adaptive_router import RouteMode
from travelwise.src.generation.generator import ResponseGenerator
from travelwise.src.retrieval.retriever import RetrievalService
from travelwise.src.retrieval.web_search import WebSearchService
from travelwise.src.utils.types import AgentResponse, RetrievedSource


class TravelWiseAgent:
    def __init__(
        self,
        retriever: RetrievalService,
        generator: ResponseGenerator,
        router: QueryRouter,
        web_search: WebSearchService | None = None,
    ) -> None:
        self.retriever = retriever
        self.generator = generator
        self.router = router
        self.web_search = web_search

    def answer(self, query: str) -> AgentResponse:
        mode = self.router.route_mode(query)
        route = "vector"
        sources: list[RetrievedSource] = []
        debug: dict = {"route_mode": mode.value}

        web_ready = self.web_search is not None and self.web_search.enabled()

        if mode == RouteMode.WEB_ONLY and web_ready:
            context, sources, debug_rows = self.web_search.search(query)
            route = "web"
            debug["web_results"] = debug_rows
            if not context:
                mode = RouteMode.VECTOR_ONLY
                debug["web_fallback_reason"] = "Web search returned no content. Falling back to vector retrieval."
        elif mode == RouteMode.WEB_ONLY and not web_ready:
            mode = RouteMode.VECTOR_ONLY
            debug["web_fallback_reason"] = "Web search unavailable (missing key or disabled)."

        if mode in {RouteMode.VECTOR_ONLY, RouteMode.VECTOR_THEN_WEB_FALLBACK}:
            context, sources, debug_rows = self.retriever.retrieve(query)
            conf = self.retriever.confidence(debug_rows)
            debug["retrieval_confidence"] = conf
            debug["retrieval"] = debug_rows
            route = "vector"

            if mode == RouteMode.VECTOR_THEN_WEB_FALLBACK and conf < 0.35 and web_ready:
                web_context, web_sources, web_debug = self.web_search.search(query)
                if web_context:
                    context = f"{context}\n\n[Web Fallback]\n{web_context}" if context else web_context
                    sources = sources + web_sources
                    debug["web_results"] = web_debug
                    debug["web_fallback_reason"] = "Low vector confidence triggered web fallback."
                    route = "vector+web"

        answer = self.generator.generate(question=query, context=context, route=route)
        debug["route"] = route
        return AgentResponse(answer=answer, route=route, sources=sources, debug=debug)
