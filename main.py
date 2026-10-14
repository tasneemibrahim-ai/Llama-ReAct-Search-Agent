import os
from dotenv import load_dotenv
from langchain_community.llms import Ollama

from agent import build_agent

load_dotenv()


def get_llm(temperature: float = 0.1) -> Ollama:
    return Ollama(model="llama3", temperature=temperature)


def run_agent(question: str, agent_executor=None) -> dict:
    """Returns dict with keys: output, steps, error."""
    if agent_executor is None:
        agent_executor = build_agent(get_llm())

    try:
        result = agent_executor.invoke({"input": question})
        steps = [
            {
                "action": action.tool,
                "action_input": action.tool_input,
                "observation": str(observation),
                "log": action.log.strip(),
            }
            for action, observation in result.get("intermediate_steps", [])
        ]
        return {"output": result["output"], "steps": steps, "error": None}
    except Exception as e:
        return {"output": None, "steps": [], "error": str(e)}


if __name__ == "__main__":
    executor = build_agent(get_llm())
    for q in [
        "What is the square root of 1764?",
        "Search for the latest AI news",
        "Calculate 15% of 2340",
    ]:
        print(f"\nQ: {q}")
        r = run_agent(q, executor)
        print(f"Error: {r['error']}" if r["error"] else f"A: {r['output']}")
