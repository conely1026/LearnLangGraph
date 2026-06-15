import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool

llm = ChatAnthropic(
    model=os.getenv("MODEL_ID"),
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
)

@tool
def multiply(a: int, b: int) -> int:
    """Multiply a and b."""
    return a * b

@tool
def add(a: int, b: int) -> int:
    """Add a and b."""
    return a + b

tools = [multiply, add]
llm_with_tools = llm.bind_tools(tools)


def call_llm(state: MessagesState) -> MessagesState:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

def route(state: MessagesState) -> str:
    last = state["messages"][-1]
    if hasattr(last, "tool_calls") and last.tool_calls:
        return "tools"
    return END

graph = StateGraph(MessagesState)
graph.add_node("call_llm", call_llm)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "call_llm")
graph.add_conditional_edges("call_llm", route)
graph.add_edge("tools", END)   # 工具跑完就结束，不回 LLM

app = graph.compile()

if __name__ == "__main__":
    cases = [
        "用一句话介绍 LangGraph",   # 不需要工具，直接回答
        "Multiply 2 and 3",          # 需要工具
        "Add 10 and 25",             # 需要工具
    ]
    for q in cases:
        print(f"问：{q}")
        result = app.invoke({"messages": [HumanMessage(content=q)]})
        for m in result["messages"]:
            m.pretty_print()
        print()
