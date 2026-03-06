from __future__ import annotations

import textwrap

import requests


class ResponseGenerator:
    def __init__(self, api_key: str | None, model: str) -> None:
        self.api_key = api_key
        self.model = model

    def _gemini_generate(self, prompt: str) -> str:
        if not self.api_key:
            raise ValueError("Missing GEMINI_API_KEY")

        url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent?key={self.api_key}"
        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=90,
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]

    def _fallback_answer(self, question: str, context: str, route: str) -> str:
        raw_notes = [line.strip() for line in context.split("\n\n") if line.strip()]
        notes = []
        for n in raw_notes:
            cleaned = n
            if "] " in cleaned[:6]:
                cleaned = cleaned.split("] ", 1)[1]
            notes.append(cleaned)

        top_notes = notes[:3] if notes else ["No strong context found for this query."]
        q = question.lower()
        itinerary_query = any(k in q for k in ["itinerary", "1-day", "2-day", "plan", "tour"])

        if itinerary_query:
            body = textwrap.dedent(
                f"""
                ### Morning
                {top_notes[0]}

                ### Afternoon
                {top_notes[1] if len(top_notes) > 1 else top_notes[0]}

                ### Evening
                {top_notes[2] if len(top_notes) > 2 else top_notes[-1]}

                ### Budget / Transit Notes
                Prefer subway/bus transfers and cluster activities by neighborhood to reduce travel time and cost.
                """
            ).strip()
        else:
            picks = "\n".join(f"- {item}" for item in top_notes)
            body = textwrap.dedent(
                f"""
                ### Recommendations
                {picks}

                ### Practical Notes
                Verify exact opening hours and ticket details the same day if your plan is time-sensitive.
                """
            ).strip()

        return (
            f"## NYC Travel Assistant\n"
            f"**Question:** {question}\n"
            f"**Route used:** {route}\n\n"
            f"{body}\n\n"
            "### Grounding\n"
            "This answer is assembled from retrieved local context chunks.\n"
            "For richer synthesis, add `GEMINI_API_KEY` in `.env`."
        ).strip()

    def generate(self, question: str, context: str, route: str) -> str:
        prompt = textwrap.dedent(
            f"""
            You are TravelWise NYC, a practical NYC travel assistant.
            Answer ONLY using the provided context. If context is limited, say so clearly.

            User question:
            {question}

            Context:
            {context}

            Style rules:
            - Keep it concise and useful.
            - For itinerary requests, use headings: Morning, Afternoon, Evening.
            - Include transit/budget notes when relevant.
            - Add a short 'Sources used' section at the end.
            - Do not invent live prices, schedules, or events.
            """
        ).strip()

        if self.api_key:
            try:
                return self._gemini_generate(prompt)
            except Exception:
                pass

        return self._fallback_answer(question=question, context=context, route=route)
