import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

from IPython.display import Image, display

model_id = os.getenv("MODEL_ID")
print(f"Model: {model_id}")

llm = ChatAnthropic(
    model=model_id,
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
)

# ── 工具 ──────────────────────────────────────────────────────────

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

# ── 节点 ──────────────────────────────────────────────────────────

sys_msg = SystemMessage(content="You are a helpful assistant tasked with performing arithmetic on a set of inputs.")
def assistant(state: MessagesState):
   return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# ── 构图 ──────────────────────────────────────────────────────────

graph = StateGraph(MessagesState)
graph.add_node("assistant", assistant)
graph.add_node("tools", ToolNode(tools))

graph.add_edge(START, "assistant")
graph.add_conditional_edges("assistant", tools_condition)
graph.add_edge("tools", "assistant")

app = graph.compile()

if __name__ == "__main__":
    result = app.invoke({"messages": [HumanMessage(content="Multiply 2 and 3")]})

    for m in result["messages"]:
        m.pretty_print()
