"""Week 9: the web UI. About 15 lines of real Streamlit, the rest is comments.

Run locally:   streamlit run app.py
Deploy:        push to GitHub, then Streamlit Community Cloud -> set OPENAI_API_KEY in Secrets.

Works offline too (FakeLLM + fallback embeddings), so your demo never hard-fails.
"""

from __future__ import annotations

import streamlit as st

from ribot.agent import run_agent
from ribot.build_index import build_index

st.set_page_config(page_title="ribot — ask my docs", page_icon="🤖")
st.title("🤖 ribot — ask my documents")


@st.cache_resource
def get_retriever():
    """Build the index once per session (cached)."""
    return build_index()


retriever = get_retriever()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ask a question about the documents..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            answer = run_agent(prompt, retriever)
        st.markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})
