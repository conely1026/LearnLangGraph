import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
from dotenv import load_dotenv
load_dotenv()

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, END, StateGraph
from langgraph.graph.message import MessagesState

llm = ChatAnthropic(
    model=os.getenv("MODEL_ID"),
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
)

# chain 的重点：节点串联，每个节点只做一件事
# 节点1 负责加系统提示，节点2 负责调 LLM

def add_system_prompt(state: MessagesState) -> MessagesState:
    system = SystemMessage(content="你是一个 LangGraph 学习助教，回答要简洁，不超过两句话。")
    return {"messages": [system] + state["messages"]}

def call_llm(state: MessagesState) -> MessagesState:
    return {"messages": [llm.invoke(state["messages"])]}

graph = StateGraph(MessagesState)
graph.add_node("add_system_prompt", add_system_prompt)
graph.add_node("call_llm", call_llm)

graph.add_edge(START, "add_system_prompt")
graph.add_edge("add_system_prompt", "call_llm")
graph.add_edge("call_llm", END)

app = graph.compile()

if __name__ == "__main__":
    questions = [
        "什么是 MessagesState？",
        "conditional edge 和普通 edge 有什么区别？",
    ]
    for q in questions:
        result = app.invoke({"messages": [HumanMessage(content=q)]})
        for m in result["messages"]:
            m.pretty_print()
        print()
