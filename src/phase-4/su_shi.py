"""
历史人物人设 Agent：苏轼（东坡居士）- Phase 4 练习
覆盖：人设系统提示、自定义 State 字段、conditional edge 意图分流

设计要点
--------
1. 纯 prompt 路线（方案 A/B）。逐字引用真迹的严格版留给 Phase 5 RAG。
2. classify 节点判断用户意图，写入 state["intent"]，conditional edge 据此分流：
       引用 quote   只报确有其作的真迹，不确定就坦白，绝不编造
       创作 create  允许即兴代拟，但强制标注“此为代拟，非东坡真迹”
       闲聊 chat     一般人设对话
3. 已知限制：纯 prompt 无法保证逐字引用准确，故 quote 节点要求诚实标注。

跑：python src/phase-4/su_shi.py
"""

import sys
sys.stdout.reconfigure(encoding="utf-8")

import os
from typing import Literal
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

load_dotenv()

# ─── Model ───────────────────────────────────────────────────────────────────
model_id = os.getenv("MODEL_ID")
print("本轮模型为"+model_id)

llm = ChatAnthropic(
    model=model_id,
    base_url=os.getenv("ANTHROPIC_BASE_URL"),
    api_key=os.getenv("ANTHROPIC_API_KEY"),
)

# ─── 人设（静态，放常量不进 state）────────────────────────────────────────────

PERSONA = """你现在扮演北宋文人苏轼（字子瞻，号东坡居士）。请始终以第一人称、用苏轼的口吻说话。

【性情】豁达乐观、幽默风趣、随遇而安。爱美食、好交友、通儒释道。
身处逆境也能自嘲解嘲，常以旷达之语化解苦闷。

【说话风格】文白相间，雅而不晦。可引宋人常语，偶发议论与感慨，但不要堆砌生僻字到读不懂。

【穿越约束】你只知道 1101 年（你辞世之年）以前的事。遇到此后或现代的事物（如手机、电脑、咖啡），
以宋人视角表达好奇、困惑或打趣，绝不假装认得，绝不泄露后世知识。"""

# ─── 事实卡（人工核对过的生平与作品清单，供 quote/chat 节点参照）──────────────
# 注意：这里给的是“可确信的篇目、背景与最广为人知的名句”。
# 整篇原文的逐字准确性留给 Phase 5 的 RAG 解决；现在 quote 节点须诚实标注。

FACT_SHEET = """【苏轼生平要点（已核对）】
- 1037 年生于眉州眉山，1101 年卒于常州。父苏洵、弟苏辙（子由），世称“三苏”。
- 1057 年中进士，主考欧阳修赏识其文。
- 1079 年“乌台诗案”下狱，1080 年贬黄州任团练副使，于东坡躬耕，自号“东坡居士”。
- 后再贬惠州、儋州（海南），晚年遇赦北归，病逝常州。
- 政治上既不满王安石新法之激进，亦不容于尽废新法的旧党，故两边不讨好，屡遭贬谪。
- 书法列“宋四家”，亦善画，更是有名的美食家（东坡肉传为其遗风）。

【确有其作的代表作（篇目 + 背景 + 最广为人知之句）】
- 《水调歌头·明月几时有》：1076 年中秋于密州作，怀念弟弟子由。名句“但愿人长久，千里共婵娟”。
- 《念奴娇·赤壁怀古》：贬黄州时游赤壁作。“大江东去，浪淘尽，千古风流人物”。
- 《前赤壁赋》《后赤壁赋》：黄州时期。
- 《题西林壁》：游庐山作。“不识庐山真面目，只缘身在此山中”。
- 《江城子·乙卯正月二十日夜记梦》：悼亡妻王弗。“十年生死两茫茫”。
- 《定风波·莫听穿林打叶声》：黄州作。“一蓑烟雨任平生”“也无风雨也无晴”。
- 《惠崇春江晚景》：题画诗。“竹外桃花三两枝，春江水暖鸭先知”。
- 岭南时期有“日啖荔枝三百颗，不辞长作岭南人”之句。"""

# ─── State ───────────────────────────────────────────────────────────────────

class SuShiState(MessagesState):
    """在 messages 之外，加一个意图字段用于条件分流。"""
    intent: str   # "quote" | "create" | "chat"

# ─── Nodes ───────────────────────────────────────────────────────────────────

def classify(state: SuShiState):
    """读最近一条用户消息，判定意图，写入 state['intent']。
    这个节点不往 messages 里加东西，只更新 intent 字段。"""
    last_user = state["messages"][-1].content

    prompt = (
        "判断用户这句话想要哪一种回应，只回答一个词：引用 / 创作 / 闲聊。\n"
        "- 引用：想听苏轼真实写过的具体作品（如“背一下念奴娇”“你写过哪些中秋的词”）\n"
        "- 创作：想让苏轼即兴新作一首（如“给我写首关于xx的诗”）\n"
        "- 闲聊：其余对话、问感受、聊生平、谈见解\n\n"
        f"用户：{last_user}\n只回答一个词："
    )
    label = llm.invoke([HumanMessage(content=prompt)]).content

    if "引用" in label:
        intent = "quote"
    elif "创作" in label:
        intent = "create"
    else:
        intent = "chat"
    return {"intent": intent}


def quote_node(state: SuShiState):
    """引用模式：只报确有其作的真迹，不确定就坦白，绝不编造。"""
    sys_prompt = PERSONA + "\n\n" + FACT_SHEET + """

【本轮任务：引用真迹】
用户想听你确实写过的作品。请：
- 只谈确有其作的篇目；拿不准整篇原文时，坦白“此篇全文我一时记不真切，恐有讹误”，宁可少引也不要编造。
- 可点明创作背景。引用名句时尽量贴合你记得的原文。
- 切勿把他人之作安到自己名下。"""
    response = llm.invoke([SystemMessage(content=sys_prompt)] + state["messages"])
    return {"messages": [response]}


def create_node(state: SuShiState):
    """创作模式：放开即兴代拟，但强制标注非真迹。"""
    sys_prompt = PERSONA + """

【本轮任务：即兴代拟】
用户想让你就某主题新作一首。请以东坡笔意即兴创作，
但务必在篇末用一行明确标注：「（此为代东坡即兴拟作，非历史真迹）」，
好教读者分得清真迹与代拟。"""
    response = llm.invoke([SystemMessage(content=sys_prompt)] + state["messages"])
    return {"messages": [response]}


def chat_node(state: SuShiState):
    """闲聊模式：一般人设对话。"""
    sys_prompt = PERSONA + "\n\n" + FACT_SHEET + """

【本轮任务：闲谈】
以苏轼的口吻与心境与对方交谈。涉及生平事实时以上面事实卡为准，不要杜撰年代与事件。"""
    response = llm.invoke([SystemMessage(content=sys_prompt)] + state["messages"])
    return {"messages": [response]}


# ─── Routing ─────────────────────────────────────────────────────────────────

def route_by_intent(state: SuShiState) -> Literal["quote", "create", "chat"]:
    return state["intent"]

# ─── Graph ───────────────────────────────────────────────────────────────────

def build_graph():
    builder = StateGraph(SuShiState)

    builder.add_node("classify", classify)
    builder.add_node("quote",  quote_node)
    builder.add_node("create", create_node)
    builder.add_node("chat",   chat_node)

    builder.add_edge(START, "classify")
    builder.add_conditional_edges("classify", route_by_intent)
    builder.add_edge("quote",  END)
    builder.add_edge("create", END)
    builder.add_edge("chat",   END)

    memory = MemorySaver()
    return builder.compile(checkpointer=memory)


# ─── Main ────────────────────────────────────────────────────────────────────

INTENT_LABEL = {"quote": "引用真迹", "create": "即兴代拟", "chat": "闲谈"}

def main():
    graph  = build_graph()
    thread = {"configurable": {"thread_id": "sushi-001"}}

    # 只流这三个“回答节点”的 token；classify 节点的 LLM 标签输出要过滤掉
    ANSWER_NODES = {"quote", "create", "chat"}

    print("【与东坡对谈】（流式，输入 q 退出）")
    print("试试：背一下念奴娇 / 给我写首关于咖啡的诗 / 你被贬黄州时是什么心情\n")

    while True:
        user_input = input("你：").strip()
        if user_input.lower() == "q":
            break

        # 组合流模式：
        #   updates  → 每个节点执行完的状态更新，用来取 classify 写入的 intent
        #   messages → 节点内 LLM 逐 token 输出，(chunk, metadata) 二元组
        printed_header = False
        for mode, data in graph.stream(
            {"messages": [HumanMessage(content=user_input)]},
            thread,
            stream_mode=["updates", "messages"],
        ):
            if mode == "updates":
                if "classify" in data:
                    intent = data["classify"]["intent"]
                    print(f"\n[意图：{INTENT_LABEL.get(intent, intent)}]")
                    print("东坡：", end="", flush=True)
                    printed_header = True

            elif mode == "messages":
                chunk, metadata = data
                # 关键：按 langgraph_node 过滤，只放行回答节点的 token
                if metadata.get("langgraph_node") in ANSWER_NODES:
                    if not printed_header:           # 兜底：万一 updates 没先到
                        print("东坡：", end="", flush=True)
                        printed_header = True
                    print(chunk.content, end="", flush=True)

        print("\n")  # 一轮结束换行


if __name__ == "__main__":
    main()
