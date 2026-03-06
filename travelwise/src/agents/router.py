from __future__ import annotations

from travelwise.src.routing.adaptive_router import AdaptiveRouter, RouteMode


class QueryRouter:
    def __init__(self, web_enabled: bool) -> None:
        self.router = AdaptiveRouter(web_enabled=web_enabled)

    def route(self, query: str) -> str:
        mode = self.router.choose_mode(query)
        if mode == RouteMode.WEB_ONLY:
            return "web"
        return "vector"

    def route_mode(self, query: str) -> RouteMode:
        return self.router.choose_mode(query)
