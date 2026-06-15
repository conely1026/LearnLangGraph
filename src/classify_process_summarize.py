import sys
sys.stdout.reconfigure(encoding="utf-8")

from typing import TypedDict, Literal

from langgraph.graph import END, StateGraph


class State(TypedDict):
    question: str
    category: str   # "definition" | "howto" | "unknown"
    answer: str
    summary: str


# ── 节点 ──────────────────────────────────────────────────────────────────────

def classify_input(state: State) -> State:
    q = state["question"].lower()
    if q.startswith("what is") or q.startswith("什么是"):
        category = "definition"
    elif q.startswith("how to") or q.startswith("如何") or q.startswith("怎么"):
        category = "howto"
    else:
        category = "unknown"
    return {**state, "category": category}


def handle_definition(state: State) -> State:
    answer = f'[定义类] 你问的是："{state["question"]}"，这是一个概念解释型问题。'
    return {**state, "answer": answer}


def handle_howto(state: State) -> State:
    answer = f'[操作类] 你问的是："{state["question"]}"，这是一个步骤指引型问题。'
    return {**state, "answer": answer}


def handle_unknown(state: State) -> State:
    answer = f'[未知类] 无法识别问题类型："{state["question"]}"。'
    return {**state, "answer": answer}


def summarize(state: State) -> State:
    summary = f"分类：{state['category']} | 回答：{state['answer']}"
    return {**state, "summary": summary}


# ── 路由 ──────────────────────────────────────────────────────────────────────

def route(state: State) -> Literal["handle_definition", "handle_howto", "handle_unknown"]:
    return f"handle_{state['category']}"


# ── 构图 ──────────────────────────────────────────────────────────────────────

def build_graph():
    graph = StateGraph(State)

    graph.add_node("classify_input", classify_input)
    graph.add_node("handle_definition", handle_definition)
    graph.add_node("handle_howto", handle_howto)
    graph.add_node("handle_unknown", handle_unknown)
    graph.add_node("summarize", summarize)

    graph.set_entry_point("classify_input")
    graph.add_conditional_edges("classify_input", route)

    graph.add_edge("handle_definition", "summarize")
    graph.add_edge("handle_howto", "summarize")
    graph.add_edge("handle_unknown", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


# ── 运行 ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = build_graph()

    questions = [
        "What is LangGraph?",
        "How to add memory to a graph?",
        "Tell me something interesting.",
    ]

    for q in questions:
        result = app.invoke({"question": q, "category": "", "answer": "", "summary": ""})
        print(result["summary"])
        print()
