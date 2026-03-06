from __future__ import annotations

from flask import Flask, jsonify, request

from travelwise.src.utils.bootstrap import create_agent
from travelwise.src.utils.config import settings


def create_app() -> Flask:
    app = Flask(__name__)
    agent = create_agent(settings)

    @app.get("/api/health")
    def health() -> tuple[dict, int]:
        return {"status": "ok"}, 200

    @app.post("/api/chat")
    def chat() -> tuple[dict, int]:
        payload = request.get_json(silent=True) or {}
        query = (payload.get("query") or "").strip()
        if not query:
            return {"error": "query is required"}, 400

        result = agent.answer(query)
        return (
            {
                "answer": result.answer,
                "route": result.route,
                "sources": [
                    {
                        "source": s.source,
                        "snippet": s.snippet,
                        "score": s.score,
                        "metadata": s.metadata,
                    }
                    for s in result.sources
                ],
                "debug": result.debug,
            },
            200,
        )

    @app.errorhandler(Exception)
    def handle_error(err: Exception):
        return jsonify({"error": str(err)}), 500

    return app
