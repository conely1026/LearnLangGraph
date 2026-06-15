import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import MessagesState


llm = ChatAnthropic(
    model=os.getenv("MODEL_ID"),
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
)

def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

llm_with_tools = llm.bind_tools([multiply])

def tool_calling_llm(state: MessagesState):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph = StateGraph(MessagesState)
graph.add_node("tool_calling_llm", tool_calling_llm)
graph.add_edge(START, "tool_calling_llm")
graph.add_edge("tool_calling_llm", END)
app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"messages": [HumanMessage(content="用一句话介绍 LangGraph")]})
    for m in result['messages']:
        m.pretty_print()

    result = app.invoke({"messages": [HumanMessage(content="Multiply 2 and 3")]})
    for m in result['messages']:
        m.pretty_print()
