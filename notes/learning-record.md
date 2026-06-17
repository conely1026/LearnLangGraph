# LangGraph 学习记录

这份记录用于放进个人云空间，作为长期可读的学习档案。它不是每天的流水账，而是把阶段、理解、卡点和下一步整理成一份可以反复回看的主记录。

详细每日记录保留在 [learning-log.md](learning-log.md)。

## 当前进度

- 当前阶段：Phase 4 Human-in-the-loop 完成（Module-3 全部跟读 + 20 题测验），准备进入 Phase 5 RAG。
- 当前主线：从基础 `StateGraph` 走到 LLM、工具调用、agent loop、checkpoint、短期记忆、SQLite 持久化，再到中断/恢复与流式输出。
- 当前代码产出：
  - `src/phase-0/hello_graph.py`：最小图和 conditional edge 入门。
  - `src/phase-1/ifelse_to_graph.py`：普通 if/else 到 graph 的对照。
  - `src/phase-2/agent.py`：ReAct 风格工具循环。
  - `src/phase-2/agent_memory.py`：MemorySaver 多轮记忆。
  - `src/phase-3/learning_assistant.py`：自定义 State、摘要记忆、SqliteSaver 持久化。
  - `src/phase-4/human_review.py`：interrupt_before 审批 agent（approve/edit/reject）。
  - `src/phase-4/su_shi.py`：苏轼人设 agent，意图分流（引用/创作/闲谈）+ 流式聊天。

## 已完成阶段

### Phase 0：环境与最小图

完成内容：

- 建立 LangGraph 学习仓库。
- 跑通不依赖 LLM 的最小 graph。
- 理解 `State`、`Node`、`Edge` 的基本关系。

关键理解：

- `State` 是 graph 运行时携带的数据。
- `Node` 是读取 state 并返回更新的函数。
- `Edge` 决定节点执行顺序。
- `invoke()` 的过程可以理解为：输入初始 state，沿着图执行节点，每个节点返回对 state 的修改，最后得到完整 state。

### Phase 1：基础图模型

完成内容：

- 给 `hello_graph.py` 加入 conditional edge。
- 把一个普通 if/else 订单处理脚本改成 LangGraph。
- 对比普通函数流程和 graph 流程。

关键理解：

- 普通函数解决“能不能跑通”。
- Graph 解决“跑通以后能不能观察、暂停、恢复、替换节点、调试路径”。
- 当流程超过 3 步、有条件分支、需要状态快照或未来可能接入记忆时，graph 的价值会开始显现。

### Phase 2：LLM 与工具调用

完成内容：

- 跟做 LangChain Academy module 1。
- 实现最小 LLM graph、chain、router、tool calling、agent loop 和 agent memory。
- 理解 tool call、observation、final answer 在 `messages` 里的流转。

关键理解：

- `MessagesState` 的 `messages` 字段是追加语义，不是覆盖语义。
- `ToolNode` 执行工具，并把结果作为 `ToolMessage` 追加回 state。
- Router 和 Agent 的核心区别是工具执行后是否回到 LLM：
  - Router：`assistant -> tools -> END`，单次工具调用。
  - Agent：`assistant -> tools -> assistant`，循环直到模型不再调用工具。

### Phase 3：持久化、检查点和记忆

完成内容：

- 跟做 module 2 的 state schema、reducer、multiple schemas、消息管理和外部记忆。
- 实现 `learning_assistant.py`。
- 使用 `SqliteSaver` 把 checkpoint 保存到 `state_db/learning_assistant.db`。

关键理解：

- `thread_id` 是会话隔离边界。
- 每次 `invoke()` 都会产生新的 checkpoint。
- checkpoint 是某一刻完整 state 的快照。
- 同一个 thread 的所有 checkpoint 组成一条可追溯的执行历史。
- 短期记忆靠 checkpointer 保存当前 thread 的 state。
- 长期记忆通常需要额外的 store，适合跨 thread 保存用户偏好、知识和语义检索内容。

## 当前稳定认知

### LangGraph 不是更复杂的 chain

Chain 更像一条固定流水线，Graph 更像一个有状态的流程运行时。Graph 的重点不是“多写几个节点”，而是给复杂流程提供状态、分支、循环、暂停、恢复和调试能力。

### State 设计决定 graph 的上限

节点只是执行步骤，真正贯穿整个系统的是 state。State 里放什么字段、哪些字段追加、哪些字段覆盖、哪些字段只在内部流转，会直接影响 graph 后续能不能扩展。

### Reducer 是理解消息流的关键

没有 reducer 的字段默认覆盖；带 reducer 的字段可以追加或自定义合并。`add_messages` 让消息历史可以按时间顺序增长，也支持同 id 消息替换和删除。

### Agent loop 的核心是路由

Agent 不神秘。它的本质是：

1. LLM 读取 state。
2. LLM 决定是否调用工具。
3. 工具结果写回 state。
4. 路由函数决定继续回到 LLM，还是结束。

### Memory 不是一个单独功能，而是一套状态保存策略

短期 memory 是 checkpoint，关注当前 thread 如何延续。长期 memory 是 store，关注跨 thread 的知识和偏好如何检索。两者不要混成一个概念。

## 仍然需要继续巩固的问题

已解决（Module-3 跟读 + 20 题测验）：

- ✅ `update_state()` 改中断点 state：`messages` 走 add_messages reducer，**不带 id 追加 / 带原 id 覆盖**；`as_node="X"` 可把更新当作 X 节点的产出。
- ✅ `get_state_history()` 用于 time travel：取历史快照的 `.config`（带 checkpoint_id）传回 `stream(None, config)` 即 replay；先 `update_state` 改再跑则 fork。
- ✅ 何时用 `interrupt`：固定卡点用 `interrupt_before`（如每次调工具审批）；按运行时条件用 `NodeInterrupt`（节点内 raise）。

仍待巩固（测验暴露的薄弱点）：

- **中断三件套**：`interrupt_before` + `checkpointer` + `thread_id`，缺 checkpointer 则中断静默失效。
- `as_node="tools"` 伪造工具产出时，`ToolMessage` 的 `tool_call_id` 必须对上原 tool_call，否则 API 报“缺响应”。
- 长期 store 的 namespace / key 应该如何设计，才不会变成杂乱缓存？（Phase 5/6）
- 从脚本走向 LangGraph Server 时，项目结构应该怎样拆？（Phase 7）

## 下一步

### Phase 4：Human-in-the-loop ✅ 完成

- 跑通 interrupt / resume：`interrupt_before` 中断 + `stream(None)` 续跑。
- `src/phase-4/human_review.py`：审批 agent，approve / edit / reject 三路径。
- `src/phase-4/su_shi.py`：苏轼人设 agent，意图分流 + 流式聊天。
- Module-3 全部 5 个 notebook 跟读完毕（breakpoints / edit-state / dynamic-breakpoints / streaming / time-travel），并做了 20 题巩固测验，易错点见 `notes/module3-pitfalls.md`。

### Phase 5：RAG（下一阶段，已规划主线）

- 目标：完成“检索资料 → 归纳引用 → 生成结构化答案”的闭环。
- 主线项目：把 `su_shi.py` 升级成 RAG 版——建苏轼语料库，引用基于检索到的真实文本，解决逐字引用准确性。
- 跟做资源：官方 `retrieval-agent-template`、`rag-research-agent-template`。

## 每次学习后怎么更新

每次学习结束，按这个格式追加到 `notes/learning-log.md`：

```md
## YYYY-MM-DD（主题）

目标：

- 今天想弄懂什么？

今日记录：

- 跑了哪些代码？
- 观察到了什么？
- 和之前理解有什么变化？

关键理解：

- 用自己的话讲一遍。

卡点：

- 哪里还不确定？

下一步：

- 下次从哪里继续？
```

当某个阶段完成后，再回到这份 `learning-record.md` 更新：

- 当前进度
- 已完成阶段
- 当前稳定认知
- 仍然需要巩固的问题
- 下一步

