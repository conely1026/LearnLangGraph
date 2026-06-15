from typing import TypedDict, Literal
from langgraph.graph import END, StateGraph

class LearningState(TypedDict):
    topic: str
    level: str
    next_step: str
    notes: list[str]

def classify(state: LearningState) -> LearningState:
    return state

def beginner_path(state: LearningState) -> LearningState:
    next_step = "Go learn basics! Start with State, Node, Edge, and Conditional Edge."
    return {
        **state,
        "next_step": next_step,
        "notes": state["notes"] + [f"Chosen path for {state['topic']}: {next_step}"],
    }

def advanced_path(state: LearningState) -> LearningState:
    next_step = "Go build an agent! Build a tool-calling agent and add checkpointing."
    return {
        **state,
        "next_step": next_step,
        "notes": state["notes"] + [f"Chosen path for {state['topic']}: {next_step}"],
    }

def route(state: LearningState) -> Literal["beginner_path", "advanced_path"]:
    level = state["level"].lower()
    if level in {"new", "beginner", "入门", "新手"}:
        return "beginner_path"
    return "advanced_path"


def summarize_plan(state: LearningState) -> LearningState:
    return {
        **state,
        "notes": state["notes"] + ["Graph finished. Read docs/02-core-concepts.md next."],
    }


def build_graph():
    graph = StateGraph(LearningState)
    graph.add_node("classify", classify)
    graph.add_node("beginner_path", beginner_path)
    graph.add_node("advanced_path", advanced_path)
    graph.add_node("summarize_plan", summarize_plan)

    graph.add_conditional_edges("classify", route)

    graph.set_entry_point("classify")
    graph.add_edge("beginner_path", "summarize_plan")
    graph.add_edge("advanced_path", "summarize_plan")
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
