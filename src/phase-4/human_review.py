"""
Human-in-the-loop 审批 Agent - Phase 4
覆盖：interrupt_before 断点、get_state 查看、update_state 改写、None 续跑

场景：一个算术 agent，在“真正调用工具之前”中断，把待执行的工具调用
摆到人面前，由人决定：
    approve  批准 → 原样执行（Approval）
    edit     改写 → 修改用户意图后重新让模型规划（Editing）
    reject   拒绝 → 跳过这次工具调用，直接收尾

跑：python src/phase-4/human_review.py
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, MessagesState, START
from langgraph.prebuilt import tools_condition, ToolNode
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# ─── Tools ───────────────────────────────────────────────────────────────────
# 用算术工具，方便和 LangChain Academy module-3 的例子对照。

def multiply(a: int, b: int) -> int:
    """Multiply a and b.

    Args:
        a: first int
        b: second int
    """
    return a * b

def add(a: int, b: int) -> int:
    """Add a and b.

    Args:
        a: first int
        b: second int
    """
    return a + b

def divide(a: int, b: int) -> float:
    """Divide a by b.

    Args:
        a: first int
        b: second int
    """
    return a / b

tools = [add, multiply, divide]

# ─── Model ───────────────────────────────────────────────────────────────────

llm = ChatAnthropic(
    model=os.getenv("MODEL_ID"),
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)
llm_with_tools = llm.bind_tools(tools)

sys_msg = SystemMessage(
    content="你是一个算术助手，负责对输入做加减乘除运算。需要计算时调用对应的工具。"
)

# ─── Nodes ───────────────────────────────────────────────────────────────────

def assistant(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# ─── Graph ───────────────────────────────────────────────────────────────────
# assistant ⇄ tools 的 ReAct 循环；关键在 compile 时挂断点：
# interrupt_before=["tools"] → 每次准备调工具前都停下，等人审批。

def build_graph():
    builder = StateGraph(MessagesState)

    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    builder.add_edge(START, "assistant")
    builder.add_conditional_edges("assistant", tools_condition)
    builder.add_edge("tools", "assistant")

    memory = MemorySaver()
    return builder.compile(interrupt_before=["tools"], checkpointer=memory)


# ─── Helpers ─────────────────────────────────────────────────────────────────

def describe_pending_tool_calls(state):
    """打印断点处待执行的工具调用，让人看清楚自己在批准什么。"""
    last = state.values["messages"][-1]
    calls = getattr(last, "tool_calls", None)
    if not calls:
        return False
    print("\n⏸  已在 tools 节点前中断，待执行的工具调用：")
    for c in calls:
        print(f"    - {c['name']}({c['args']})")
    return True


def run_until_end(graph, thread):
    """从当前 checkpoint 续跑（input=None），打印每一步，直到再次中断或结束。"""
    for event in graph.stream(None, thread, stream_mode="values"):
        event["messages"][-1].pretty_print()


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    graph  = build_graph()
    thread = {"configurable": {"thread_id": "review-001"}}

    print("算术审批 agent 已启动（输入 q 退出）")
    print("调工具前会中断，可选择 approve / edit / reject\n")

    while True:
        user_input = input("你：").strip()
        if user_input.lower() == "q":
            break

        # 第一次：带真实输入跑，直到 tools 断点停下（或模型不调工具直接结束）
        for event in graph.stream(
            {"messages": [HumanMessage(content=user_input)]},
            thread,
            stream_mode="values",
        ):
            event["messages"][-1].pretty_print()

        # 循环处理可能连续出现的多次工具调用（每次都会停在断点）
        while True:
            state = graph.get_state(thread)

            # state.next 为空 = 没有待执行节点 = 已经跑到 END
            if not state.next:
                break

            if not describe_pending_tool_calls(state):
                # 停在 tools 前却没有 tool_calls，理论上不会发生，保险退出
                break

            choice = input("\n[approve/edit/reject]：").strip().lower()

            if choice == "approve":
                # Approval：原样续跑，执行工具
                run_until_end(graph, thread)

            elif choice == "edit":
                # Editing：追加一条新的人类消息纠正意图，
                # 再续跑——模型会基于新消息重新规划工具调用。
                correction = input("改写成：").strip()
                graph.update_state(
                    thread,
                    {"messages": [HumanMessage(content=correction)]},
                )
                # 注意：update_state 默认 as_node 为最近执行的节点（assistant），
                # 续跑会重新进入 assistant 让模型读到纠正消息后重新决策。
                run_until_end(graph, thread)

            elif choice == "reject":
                # 拒绝：用 update_state 假装“工具已执行”，写回一句说明，
                # 让 assistant 据此收尾，而不真正运行工具。
                last_call = state.values["messages"][-1].tool_calls[0]
                graph.update_state(
                    thread,
                    {"messages": [ToolMessage(
                        content="用户拒绝了这次工具调用。",
                        tool_call_id=last_call["id"],
                    )]},
                    as_node="tools",
                )
                run_until_end(graph, thread)

            else:
                print("无效输入，请输入 approve / edit / reject")
                continue

        print()  # 一轮结束空行


if __name__ == "__main__":
    main()
