from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RetrievedSource:
    source: str
    snippet: str
    score: float | None = None
    metadata: dict = field(default_factory=dict)


@dataclass
class AgentResponse:
    answer: str
    route: str
    sources: list[RetrievedSource]
    debug: dict
