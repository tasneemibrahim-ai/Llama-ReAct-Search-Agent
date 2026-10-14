import math
import os

from langchain.tools import Tool
from langchain_community.tools.tavily_search import TavilySearchResults


def _calculator(expression: str) -> str:
    try:
        safe_globals = {k: getattr(math, k) for k in dir(math) if not k.startswith("_")}
        safe_globals["__builtins__"] = {}
        result = eval(expression, safe_globals)  # noqa: S307
        return str(result)
    except Exception as e:
        return f"Calculator error: {e}"


def _file_reader(filepath: str) -> str:
    filepath = filepath.strip().strip('"').strip("'")
    if not os.path.exists(filepath):
        return f"File not found: {filepath}"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read(5000) or "File is empty."
    except Exception as e:
        return f"File read error: {e}"


def _tavily_search(query: str) -> str:
    try:
        tavily = TavilySearchResults(max_results=3)
        results = tavily.invoke(query)
        if not results:
            return "No results found."
        output = []
        for r in results:
            output.append(f"Source: {r.get('url', 'N/A')}\n{r.get('content', '')}")
        return "\n\n".join(output)
    except Exception as e:
        return f"Search error: {e}"


def get_tools() -> list:
    return [
        Tool(
            name="Calculator",
            func=_calculator,
            description=(
                "Evaluates a mathematical expression. "
                "Input must be a valid Python math expression. "
                "Examples: '2 + 2', 'sqrt(144)', '3 ** 4', '(10 * 5) / 2'"
            ),
        ),
        Tool(
            name="WebSearch",
            func=_tavily_search,
            description=(
                "Searches the web for current, accurate information using Tavily. "
                "Input should be a concise search query string. "
                "Use for factual questions, recent events, live data, or statistics."
            ),
        ),
        Tool(
            name="FileReader",
            func=_file_reader,
            description=(
                "Reads content from a local text file. "
                "Input must be the full absolute file path. "
                "Example: '/home/user/notes.txt'"
            ),
        ),
    ]
