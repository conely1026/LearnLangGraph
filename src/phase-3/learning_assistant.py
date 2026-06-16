"""
学习助教 Agent - Phase 3
覆盖：自定义 State、摘要记忆、MemorySaver 持久化

框架已搭好，关键实现留空，完成后即为 Phase 3 验收。
"""

import os
import sqlite3
from typing import Literal
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage, RemoveMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

load_dotenv()

# ─── DataBase ────────────────────────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # src/phase-3/
SRC_DIR  = os.path.dirname(os.path.dirname(BASE_DIR))  # 项目根目录
db_path  = os.path.join(SRC_DIR, "state_db", "learning_assistant.db")
os.makedirs(os.path.dirname(db_path), exist_ok=True)
conn = sqlite3.connect(db_path, check_same_thread=False)

# ─── Model ───────────────────────────────────────────────────────────────────

llm = ChatAnthropic(
    model=os.getenv("MODEL_ID"),
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

# ─── State ───────────────────────────────────────────────────────────────────

class LearningState(MessagesState):
    """
    在 MessagesState（内置 messages + add_messages reducer）基础上
    扩展学习助教专用字段。
    """
    topic: str          # 当前学习主题，e.g. "LangGraph"
    level: str          # 学习水平：beginner / intermediate / advanced
    summary: str        # 旧对话的压缩摘要（摘要记忆模式）

# ─── Nodes ───────────────────────────────────────────────────────────────────

def call_model(state: LearningState):
    summary = state.get("summary", "")
    topic   = state.get("topic", "未指定")
    level   = state.get("level", "beginner")

    system_prompt = (
        f"你是一位耐心的学习助教，当前帮助学习者学习「{topic}」。\n"
        f"学习者水平：{level}。请根据水平调整解释的深度和用语。"
    )
    if summary:
        system_prompt += f"\n\n以下是之前对话的摘要，请保持上下文连贯：\n{summary}"

    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": [response]}


def summarize_conversation(state: LearningState):
    """
    摘要节点。生成/更新对话摘要，然后清理旧消息只保留最近 2 条。
    """
    summary = state.get("summary", "")

    if summary:
        # A summary already exists
        summary_prompt = (
            f"This is summary of the conversation to date: {summary}\n\n"
            "Extend the summary by taking into account the new messages above:"
        )
    else:
        summary_prompt = "Create a summary of the conversation above:"

    messages  = state["messages"] + [HumanMessage(content=summary_prompt)]
    response  = llm.invoke(messages)

    # 删旧消息，只留最后 2 条（保留一问一答的落脚点）
    delete_messages = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    return {"summary": response.content, "messages": delete_messages}


# ─── Routing ─────────────────────────────────────────────────────────────────

def should_continue(state: LearningState) -> Literal["summarize_conversation", "__end__"]:
    messages = state["messages"]
    
    # If there are more than six messages, then we summarize the conversation
    if len(messages) > 6:
        return "summarize_conversation"
    
    return END


# ─── Graph ───────────────────────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(LearningState)

    builder.add_node("conversation",           call_model)
    builder.add_node("summarize_conversation", summarize_conversation)

    builder.add_edge(START, "conversation")
    builder.add_conditional_edges("conversation", should_continue)
    builder.add_edge("summarize_conversation", END)

    memory = SqliteSaver(conn)
    return builder.compile(checkpointer=memory)


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    graph  = build_graph()
    config = {"configurable": {"thread_id": "learner-001"}}

    # topic/level 只在首次启动时写入，后续从 checkpoint 读取
    existing = graph.get_state(config).values
    if not existing.get("topic"):
        graph.update_state(config, {"topic": "LangGraph", "level": "beginner"})

    print("学习助教已启动（输入 q 退出）\n")

    while True:
        user_input = input("你：").strip()
        if user_input.lower() == "q":
            break

        output = graph.invoke({"messages": [HumanMessage(content=user_input)]}, config)
        print(f"\n助教：{output['messages'][-1].content}\n")

        # 打印当前 state 摘要，用于观察何时触发摘要节点
        current = graph.get_state(config).values
        msg_count = len(current.get("messages", []))
        summary   = current.get("summary", "")
        print(f"[消息数: {msg_count} | 摘要: {'有' if summary else '无'}]")
        if summary:
            print(f"[摘要内容: {summary}...]\n")


if __name__ == "__main__":
    main()
