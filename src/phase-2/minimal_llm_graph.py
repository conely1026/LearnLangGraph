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


def call_llm(state: MessagesState) -> MessagesState:
    return {"messages": [llm.invoke(state["messages"])]}


graph = StateGraph(MessagesState)
graph.add_node("call_llm", call_llm)
graph.add_edge(START, "call_llm")
graph.add_edge("call_llm", END)
app = graph.compile()


if __name__ == "__main__":
    result = app.invoke({"messages": [HumanMessage(content="用一句话介绍 LangGraph")]})
    print(result["messages"][-1].content)
