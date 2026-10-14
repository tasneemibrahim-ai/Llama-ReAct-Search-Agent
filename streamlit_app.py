import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from langchain_community.llms import Ollama

from agent import build_agent
from main import run_agent


def get_llm(temperature: float = 0.1) -> Ollama:
    return Ollama(model="llama3", temperature=temperature)


st.set_page_config(page_title="Llama Agent", page_icon="🤖", layout="wide")
st.title("🤖 Llama ReAct Agent")
st.caption("Multi-step reasoning · Calculator · Tavily Web Search · File Reader · Powered by Ollama + LangChain")

# Validate Tavily key on startup
if not os.getenv("TAVILY_API_KEY"):
    st.error("❌ TAVILY_API_KEY not found. Add it to your .env file and restart the app.")
    st.code("TAVILY_API_KEY=tvly-your-key-here", language="bash")
    st.stop()

# Init agent once per session
if "agent_executor" not in st.session_state:
    with st.spinner("Loading Llama3 agent..."):
        try:
            st.session_state.agent_executor = build_agent(get_llm())
            st.session_state.chat_history = []
        except Exception as e:
            st.error(f"Failed to load agent: {e}")
            st.stop()

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    show_steps = st.toggle("Show reasoning steps", value=True)

    st.divider()
    st.subheader("💡 Example Queries")
    examples = [
        "What is the square root of 1764?",
        "Search for the current population of Tokyo",
        "Calculate 23% of 4750 and then double it",
        "What is 2 to the power of 16?",
        "Search for the latest news about OpenAI",
        "What is the current price of Bitcoin?",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["pending_query"] = ex

    st.divider()
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.agent_executor = build_agent(get_llm())
        st.rerun()

    st.divider()
    st.subheader("🛠️ Available Tools")
    st.markdown(
        "- 🧮 **Calculator** — math expressions\n"
        "- 🌐 **WebSearch** — Tavily (reliable live search)\n"
        "- 📄 **FileReader** — read local text files"
    )

# Render existing chat history
for msg in st.session_state.get("chat_history", []):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and show_steps and msg.get("steps"):
            with st.expander("🔍 Reasoning Steps", expanded=False):
                for i, step in enumerate(msg["steps"], 1):
                    st.markdown(f"**Step {i} — {step['action']}**")
                    st.code(f"Input: {step['action_input']}", language="text")
                    st.info(f"Observation: {step['observation'][:500]}")

# Handle sidebar button pre-fill
pending = st.session_state.pop("pending_query", "")
user_input = st.chat_input("Ask anything...") or pending

if user_input:
    with st.chat_message("user"):
        st.markdown(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            result = run_agent(user_input, st.session_state.agent_executor)

        if result["error"]:
            st.error(f"❌ Agent error: {result['error']}")
            response_text = f"Error: {result['error']}"
            steps = []
        else:
            response_text = result["output"]
            steps = result["steps"]
            st.markdown(response_text)
            if show_steps and steps:
                with st.expander("🔍 Reasoning Steps", expanded=False):
                    for i, step in enumerate(steps, 1):
                        st.markdown(f"**Step {i} — {step['action']}**")
                        st.code(f"Input: {step['action_input']}", language="text")
                        st.info(f"Observation: {step['observation'][:500]}")

    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response_text,
        "steps": steps,
    })