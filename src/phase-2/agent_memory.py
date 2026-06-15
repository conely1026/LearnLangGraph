import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langgraph.graph import START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.memory import MemorySaver

model_id = os.getenv("MODEL_ID")
llm = ChatAnthropic(
    model=model_id,
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
)

# ── 记忆 ──────────────────────────────────────────────────────────

memory = MemorySaver()

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

# ── 构图（与 agent.py 相同）────────────────────────────────────────

graph = StateGraph(MessagesState)
graph.add_node("assistant", assistant)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "assistant")
graph.add_conditional_edges("assistant", tools_condition)
graph.add_edge("tools", "assistant")

# 初始化 MemorySaver，compile 时传入 checkpointer
app = graph.compile(checkpointer=memory)

# ── 多轮对话 ──────────────────────────────────────────────────────

config = {"configurable": {"thread_id": "1"}}

if __name__ == "__main__":
    # 第一轮
    print("=== 第一轮 ===")
    # TODO: 用 config 调用 app.invoke，提问 "Multiply 2 and 3"
    messages = app.invoke({"messages": [HumanMessage(content="Multiply 2 and 3")]},config)
    for m in messages['messages']:
        m.pretty_print()

    # 第二轮：不重复背景，直接问"再加上 10 是多少"，看它是否记得上一轮结果
    print("=== 第二轮 ===")
    # TODO: 用同一 config 调用 app.invoke，提问 "把上面的结果再加 10"
    messages = app.invoke({"messages": [HumanMessage(content="add that by 10")]},config)
    messages['messages'][-1].pretty_print()

    # 第三轮：换一个 thread_id，验证记忆隔离
    print("=== 第三轮（新 thread）===")
    # TODO: 换新 thread_id，提问同样问题，观察它是否还记得前两轮
    messages = app.invoke({"messages": [HumanMessage(content="add that by 10")]},{"configurable": {"thread_id": "2"}})
    messages['messages'][-1].pretty_print()
