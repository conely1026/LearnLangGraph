from typing import TypedDict

from langgraph.graph import END, StateGraph


class LearningState(TypedDict):
    topic: str
    level: str
    next_step: str
    notes: list[str]


def choose_path(state: LearningState) -> LearningState:
    level = state["level"].lower()
    if level in {"new", "beginner", "入门", "新手"}:
        next_step = "Start with State, Node, Edge, and Conditional Edge."
    else:
        next_step = "Build a tool-calling agent and add checkpointing."

    return {
        **state,
        "next_step": next_step,
        "notes": state["notes"] + [f"Chosen path for {state['topic']}: {next_step}"],
    }


def summarize_plan(state: LearningState) -> LearningState:
    return {
        **state,
        "notes": state["notes"] + ["Graph finished. Read docs/02-core-concepts.md next."],
    }


def build_graph():
    graph = StateGraph(LearningState)
    graph.add_node("choose_path", choose_path)
    graph.add_node("summarize_plan", summarize_plan)

    graph.set_entry_point("choose_path")
    graph.add_edge("choose_path", "summarize_plan")
    graph.add_edge("summarize_plan", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()
    result = app.invoke(
        {
            "topic": "LangGraph",
            "level": "beginner",
            "next_step": "",
            "notes": [],
        }
    )

    print("Next step:", result["next_step"])
    print("Notes:")
    for note in result["notes"]:
        print("-", note)

