from __future__ import annotations

from dataclasses import asdict

from travelwise.src.utils.bootstrap import create_agent
from travelwise.src.utils.config import settings

TEST_QUERIES = [
    "Plan me a 1-day food tour in Manhattan",
    "What are the top museums near Central Park?",
    "Suggest a budget-friendly 2-day NYC itinerary",
    "What are the best pizza spots in Brooklyn?",
    "Things to do near Times Square in the evening",
]


def run_evaluation() -> None:
    agent = create_agent(settings)
    print("=== TravelWise NYC Evaluation ===")
    for i, q in enumerate(TEST_QUERIES, start=1):
        result = agent.answer(q)
        print(f"\n[{i}] Query: {q}")
        print(f"Route: {result.route}")
        print(f"Sources retrieved: {len(result.sources)}")
        for src in result.sources[:3]:
            print(f"- {src.source} | score={src.score}")
        print("Answer preview:")
        print(result.answer[:450].replace("\n", " "))
        print("Debug keys:", list(result.debug.keys()))


if __name__ == "__main__":
    run_evaluation()
