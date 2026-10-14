from langchain.agents import AgentExecutor, create_react_agent
from langchain.prompts import PromptTemplate
from langchain_core.language_models import BaseLLM

from tools import get_tools
from memory import get_memory

REACT_TEMPLATE = """You are a helpful AI assistant with access to tools. Use ReAct reasoning.

Available tools:
{tools}

Tool names: {tool_names}

Conversation history:
{chat_history}

Use this EXACT format:

Question: the input question you must answer
Thought: think step by step about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (repeat Thought/Action/Action Input/Observation as needed)
Thought: I now know the final answer
Final Answer: the final answer to the original question

Begin!

Question: {input}
Thought: {agent_scratchpad}"""


def build_agent(llm: BaseLLM) -> AgentExecutor:
    tools = get_tools()
    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "chat_history", "tools", "tool_names"],
        template=REACT_TEMPLATE,
    )
    agent = create_react_agent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=get_memory(),
        verbose=True,
        handle_parsing_errors=True,
        max_iterations=8,
        return_intermediate_steps=True,
        output_key="output",
    )
