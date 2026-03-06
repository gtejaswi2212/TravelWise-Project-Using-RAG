from __future__ import annotations

from enum import Enum


class RouteMode(str, Enum):
    VECTOR_ONLY = "VECTOR_ONLY"
    WEB_ONLY = "WEB_ONLY"
    VECTOR_THEN_WEB_FALLBACK = "VECTOR_THEN_WEB_FALLBACK"


REALTIME_HINTS = {
    "today",
    "tonight",
    "current",
    "right now",
    "open now",
    "event",
    "weather",
    "news",
    "delay",
    "closure",
    "ticket",
    "hours",
    "price",
}


class AdaptiveRouter:
    def __init__(self, web_enabled: bool) -> None:
        self.web_enabled = web_enabled

    def choose_mode(self, query: str) -> RouteMode:
        q = query.lower()
        realtime = any(hint in q for hint in REALTIME_HINTS)

        if realtime and self.web_enabled:
            return RouteMode.WEB_ONLY
        if realtime and not self.web_enabled:
            return RouteMode.VECTOR_ONLY
        if self.web_enabled:
            return RouteMode.VECTOR_THEN_WEB_FALLBACK
        return RouteMode.VECTOR_ONLY
