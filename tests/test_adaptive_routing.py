from travelwise.src.agents.router import QueryRouter
from travelwise.src.routing.adaptive_router import RouteMode


def test_route_mode_dynamic_query_uses_web_when_enabled():
    router = QueryRouter(web_enabled=True)
    mode = router.route_mode("What events are happening tonight in NYC?")
    assert mode == RouteMode.WEB_ONLY


def test_route_mode_static_query_prefers_vector_then_web_when_enabled():
    router = QueryRouter(web_enabled=True)
    mode = router.route_mode("Plan me a 1-day food tour in Manhattan")
    assert mode == RouteMode.VECTOR_THEN_WEB_FALLBACK


def test_route_mode_without_web_key_is_vector_only():
    router = QueryRouter(web_enabled=False)
    mode = router.route_mode("What events are happening tonight in NYC?")
    assert mode == RouteMode.VECTOR_ONLY
