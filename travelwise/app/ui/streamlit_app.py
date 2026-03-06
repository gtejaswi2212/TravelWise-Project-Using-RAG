from __future__ import annotations

import streamlit as st

from travelwise.src.utils.bootstrap import create_agent
from travelwise.src.utils.config import settings, validate_settings

st.set_page_config(page_title="TravelWise NYC", page_icon="🗽", layout="wide")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent" not in st.session_state:
    st.session_state.agent = create_agent(settings)

st.markdown(
    """
    <style>
    .tw-hero {
        background: linear-gradient(135deg, #12343b 0%, #2d545e 40%, #e1b382 100%);
        border-radius: 16px;
        color: #f5f5f5;
        padding: 22px 26px;
        margin-bottom: 14px;
    }
    .tw-card {
        border: 1px solid #e6e2dd;
        border-radius: 12px;
        padding: 10px 12px;
        margin-bottom: 8px;
        background: #fffdfa;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class='tw-hero'>
      <h2 style='margin:0'>🗽 TravelWise: Adaptive RAG Travel Assistant for NYC</h2>
      <p style='margin:6px 0 0 0'>An AI travel assistant that combines vector retrieval over curated travel knowledge with live web search via Tavily for fresh, grounded answers.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

col_chat, col_side = st.columns([2.2, 1], gap="large")

with col_side:
    st.subheader("System status")
    warnings = validate_settings(settings)
    st.write(f"- Vector index: `{settings.vector_index_dir}`")
    st.write(f"- Web fallback: `{'enabled' if settings.use_web_fallback else 'disabled'}`")
    st.write(f"- Tavily key: `{'configured' if settings.tavily_api_key else 'missing'}`")
    st.write(f"- Gemini key: `{'configured' if settings.gemini_api_key else 'missing (fallback mode)'}`")
    if warnings:
        with st.expander("Config warnings", expanded=False):
            for w in warnings:
                st.warning(w)

    st.divider()
    st.subheader("Try prompts")
    samples = [
        "Plan me a 1-day food tour in Manhattan",
        "What are the top museums near Central Park?",
        "Suggest a budget-friendly 2-day NYC itinerary",
        "What are the best pizza spots in Brooklyn?",
        "Things to do near Times Square in the evening",
    ]
    for s in samples:
        if st.button(s, key=f"sample-{s}"):
            st.session_state.pending_prompt = s

    st.divider()
    if st.button("Reset conversation"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Tip: Add `TAVILY_API_KEY` + `GEMINI_API_KEY` in `.env` for full adaptive behavior.")

with col_chat:
    st.subheader("Chat")
    if not st.session_state.messages:
        st.info("Ask NYC travel questions. Use sample prompts to demo adaptive routing, grounded retrieval, and sources.")
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Ask a NYC travel question")
    if not prompt and st.session_state.get("pending_prompt"):
        prompt = st.session_state.pop("pending_prompt")

    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Retrieving sources and building answer..."):
                try:
                    result = st.session_state.agent.answer(prompt)
                    st.markdown(result.answer)

                    mode = result.debug.get("route_mode", "n/a")
                    st.markdown(f"**Retrieval mode:** `{mode}`")
                    st.markdown(f"**Execution path:** `{result.route}`")

                    if result.sources:
                        with st.expander("Sources used", expanded=False):
                            for src in result.sources:
                                score = f" | score={src.score:.3f}" if src.score is not None else ""
                                url = src.metadata.get("url")
                                source_line = f"<b>{src.source}</b>{score}"
                                if url:
                                    source_line += f"<br><a href='{url}' target='_blank'>{url}</a>"
                                st.markdown(
                                    f"<div class='tw-card'>{source_line}<br>{src.snippet}</div>",
                                    unsafe_allow_html=True,
                                )

                    with st.expander("Debug panel", expanded=False):
                        st.json(result.debug)

                    st.session_state.messages.append({"role": "assistant", "content": result.answer})
                except Exception as err:
                    error_text = f"I hit an error while generating this response: {err}"
                    st.error(error_text)
                    st.session_state.messages.append({"role": "assistant", "content": error_text})
