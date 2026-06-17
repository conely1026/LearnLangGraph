# Module-3 易错点速查

测验暴露的高频坑，按"一句话纠正"整理，回看用。完整题目见 `module3-quiz.md`。

## 中断机制

1. **中断三件套**：`interrupt_before` + `checkpointer` + `thread_id`，缺一不中断。
   最易漏 `checkpointer`——没有它，中断**静默失效**，图一路跑到底。

2. **`interrupt_before` vs `NodeInterrupt` 的续跑行为**（最易混）：
   - `interrupt_before`：`stream(None)` = **迈过门口往下走**。
   - `NodeInterrupt`：`stream(None)` = **重跑该节点**，触发条件没消就再次中断 → 原地卡死。
   - 解除 `NodeInterrupt` 必须 **`update_state` 改掉触发条件**，不是改代码。

3. `NodeInterrupt` 的中断原因记录在 `state.tasks[].interrupts`，不是 `state.next`。

## 改 state

4. **追加 vs 覆盖看消息 `id`**，与 `thread_id` 无关：不带 id 追加，带原 id 覆盖。

5. **`as_node="X"`** = 把更新伪造成 X 节点的产出，让图跳过它继续往下。
   reject 路径塞 `ToolMessage` 时，`tool_call_id` **必须对上原 tool_call**，否则 API 报"缺响应"。

## 流式

6. **`messages` 模式会流出每个调 LLM 节点的 token**（苏轼的 classify 也吐"引用/创作/闲聊"标签）。
   多节点图必须按 `metadata["langgraph_node"]` 过滤，只放行回答节点。

## time-travel

7. **Replay vs Fork 的唯一判定**：传回旧 config 前**有没有 `update_state` 改过 state**。没改=Replay，改了=Fork。
8. 传回的必须是**历史快照的 `.config`**（带 checkpoint_id），传普通 `thread` 永远指向最新。

## 看题/术语习惯

- `AIMessage`（带 tool_calls）≠ "tool_use" 块——问"消息类型"答 AIMessage。
- 看清题目数字（"Multiply 5 and 3" 是 5×3=15，不是 5×5）。
