# Module-3 巩固题库（Human-in-the-loop / Streaming / Time-travel）

20 题，分三类：概念辨析 / 读代码 / 场景诊断。答案折叠在每题下方，自测时先盖住。
首次作答记录见 `learning-log.md`（2026-06-17）。

---

## A. 概念辨析（8 题）

**A1.** `stream_mode` 的 `values` / `updates` / `messages` 各产出什么？

> - `values`：每个节点执行后的**完整 state**。
> - `updates`：每个节点这一步产生的**增量更新**（`{节点名: 改了的字段}`）。
> - `messages`：节点内 LLM 的**逐 token 流**，每个 event 是 `(chunk, metadata)`。

**A2.** `interrupt_before=["tools"]` 与 `raise NodeInterrupt(...)` 的区别？

> - 定义位置：前者编译期参数；后者运行时在节点函数内部 raise。
> - 时机：前者每次到该节点门口都停（静态）；后者按运行时条件停（动态），可带原因消息。
> - **续跑行为**：前者 `stream(None)` 迈过门口往下走；后者 `stream(None)` **重跑该节点**，条件没变就再次中断。

**A3.** 把旧 checkpoint 的 config 传回续跑，什么是 Replay、什么是 Fork？唯一判定依据？

> 唯一依据 = 传回旧 config **之前有没有 `update_state` 改过 state**。
> - 没改 → 图认得已执行过 → **Replay**（重放）。
> - 改了 → 生成新分支 checkpoint、图没见过 → **Fork**（真跑）。

**A4.** `update_state` 改 `messages` 时，何时追加、何时覆盖？

> 看消息**有没有带 `id`**（与 thread_id 无关）：不带 id → 追加；带原 id → 覆盖那条。这是 `add_messages` reducer 的规则。

**A5.** `get_state` vs `get_state_history`？后者排列顺序？

> `get_state(thread)` 取**当前最新**快照；`get_state_history(thread)` 取**全部历史**快照，**新→旧**排列。

**A6.** `update_state(..., as_node="human_feedback")` 中 `as_node` 的作用？去掉会怎样？

> 把这次更新**当作该节点的产出**，让图认为该节点已执行，从而沿其出边继续。去掉则图不会把写入归属给该节点，无法正确推进。

**A7.** time-travel 里 `thread_id` 和 `checkpoint_id` 各选什么？

> `thread_id` 选**哪条会话**；`checkpoint_id` 选**这条会话时间线上的哪一个历史快照（存档点）**。

**A8.** 苏轼的 conditional edge 分流 vs human-in-the-loop 中断，本质区别？

> 前者是图**自己读 state 自动选路、全程不停、人不参与**；后者是图**停下来把控制权交给人**（看 / 改 / 批准）。

---

## B. 读代码（7 题）

**B1.** `step_2` 内 `if len(state['input'])>5: raise NodeInterrupt(...)`，输入 `"hello world"`。第一次 stream 停在哪？紧接着 `stream(None)` 会怎样？

> 停在 `step_2`。直接 `stream(None)` 会**从头重跑 step_2**，`11>5` 仍成立 → 再次中断 → 原地卡死。`stream(values)` 只重发当前 state `{'input':'hello world'}`，`next` 仍是 `('step_2',)`。**不会打印历史快照**（那是 get_state_history 的事）。

**B2.** 接 B1，要跑完 step_2/step_3，续跑前加哪一行？

> `graph.update_state(thread, {"input": "hi"})`（改 state 让条件不成立），再 `stream(None)`。注意是改 state，不是改代码。

**B3.** `compile(interrupt_before=["tools"], checkpointer=...)`，输入"Multiply 2 and 3"跑到中断。`get_state(thread).next`？最后一条消息类型？

> `next` = `('tools',)`。最后一条是 **`AIMessage`（带 `tool_calls`）**——模型已决定调工具但还没执行；ToolMessage 要等 tools 节点跑完才有。

**B4.** 原本 1 条 `Human(id=X)`，两种 update_state 后各几条？甲：`{"messages":[HumanMessage("改成3和3")]}`；乙：`{"messages":[HumanMessage("改成3和3", id=X)]}`

> 甲 → 2 条（追加）；乙 → 1 条（覆盖）。

**B5.** 苏轼流式里删掉 `langgraph_node` 过滤，屏幕上会多看到什么？

> 会先闪过 classify 节点吐的**分类标签**（"引用"/"创作"/"闲聊"），然后才是正文。因为 messages 模式会流出每个调 LLM 节点的 token。

**B6.** reject 分支 `update_state({"messages":[ToolMessage(content="拒绝", tool_call_id=last_call["id"])]}, as_node="tools")`：(a) 为何工具没真跑？(b) tool_call_id 写错会怎样？

> (a) `as_node="tools"` 让图**以为 tools 节点已产出结果**（我们手塞的 ToolMessage），于是跳过真执行直接走到 assistant。工具函数没被调用。
> (b) 上条 AIMessage 的 tool_call 找不到匹配的 tool_result → Anthropic 要求每个 tool_call 必须有对应响应 → 后续调模型时 **API 报错**（“缺响应”）。

**B7.** Fork：`update_state(to_fork.config, {"messages":[HumanMessage("Multiply 5 and 3", id=原id)]})` 后跑。算几乘几？重放还是真跑？

> 算 **5×3=15**（看清 content 是 "Multiply 5 and 3"）。**真跑**——改了 state 生成新分支 checkpoint，图没执行过。

---

## C. 场景诊断（5 题）

**C1.** "NodeInterrupt 中断后我一直 stream(None)，每次都回到同一节点又停，像卡死。"

> state 没改 → 条件仍成立 → 反复中断。修：先 `update_state` 改掉触发条件，再续跑。

**C2.** "加了 `interrupt_before=['tools']`，但根本不停，直接把工具跑完了。"

> 最可能：**compile 时漏了 `checkpointer`**（中断需把 state 存进 checkpoint，没 checkpointer 则静默失效）。次要：config 没给 `thread_id`；节点名拼错（如 "tool" ≠ "tools"）。**中断三件套：interrupt_before + checkpointer + thread_id。**

**C3.** "用 update_state 想改掉上一句问题，结果模型看到两个问题。"

> 没带原消息 id → add_messages 追加而非覆盖。修：带上原 id。

**C4.** "想 time-travel 回上一轮重问，但每次都接着最新跑。"

> 传错了 config——传了普通 `thread`（永远指向最新）。应传**那个历史快照的 `.config`**（带 checkpoint_id）。

**C5.** "苏轼流式回答先闪过'闲聊'两字再正文。"

> messages 模式没过滤 classify 的标签 token。修：`if metadata["langgraph_node"] in {"quote","create","chat"}` 只放行回答节点。
