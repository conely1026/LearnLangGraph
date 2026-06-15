# Learning Log

## 2026-06-15

目标：

- 初始化 LangGraph 学习仓库。
- 跑通最小 graph。
- 制定 4 周学习路径。

今日记录：

- LangGraph 更像一个有状态工作流运行时，而不是简单 chain。
- 学习要从 StateGraph 开始，不急着一开始就上多 agent。
- `src/hello_graph.py` 的 state 有 `topic`、`level`、`next_step`、`notes` 四个字段，分别表示学习主题、当前水平、下一步建议和执行记录。
- 被注册成 node 的函数是 `choose_path` 和 `summarize_plan`。`choose_path` 根据 `level` 设置 `next_step` 并追加记录；`summarize_plan` 在结束前继续给 `notes` 追加一条固定记录。
- edge 通过 `set_entry_point` 和 `add_edge` 决定执行顺序。本例从 `choose_path` 开始，然后进入 `summarize_plan`，最后到 `END` 结束。

卡点：

- Python 语法还需要熟悉：`TypedDict`、`**state`、f-string、函数类型标注。

明日计划：

- 跟做 LangChain Academy Introduction to LangGraph 的 module 0-1。
- 把 `src/hello_graph.py` 改成一个带 conditional edge 的版本。

---

## 2026-06-15（续）

目标：

- 为 `hello_graph.py` 添加 conditional edge。

今日记录：

- `add_conditional_edges(from_node, router_fn)` 是关键 API：从某节点出发，由路由函数在运行时决定走哪个分支。
- 路由函数只接收 state、只返回节点名字符串，不修改 state（CQS：查询和命令分离）。
- 用 `Literal["node_a", "node_b"]` 标注路由函数返回值，IDE 能检查节点名合法性。
- 典型结构是钻石形：入口节点 → conditional edge → 多个分支节点 → 汇聚节点 → END。
- `hello_graph.py` 现在的路径：`classify → (route) → beginner_path / advanced_path → summarize_plan → END`。

卡点：无。

下一步：

- 跟做 LangChain Academy module 1（Router、Agent、Memory 部分）。
- 第 1 阶段验收：能画出 graph 执行路径，能说清楚为什么这里用 graph 而不是普通函数。

---

## 2026-06-15（Phase 1 收尾）

目标：

- 把一个普通 if/else 脚本改成 LangGraph，理解"为什么用 graph"。

今日记录：

- `src/ifelse_to_graph.py`：订单处理场景，普通函数和 graph 两个版本并排对比，结果一致。
- 图结构：`check_stock → (route) → calc_price / reject_order`，通过路径收拢到 END。
- graph 版本比 if/else 多写了代码，但换来了：
  - 每个节点可以独立测试
  - state 在任意节点可被快照（后续加 checkpointer 不改节点代码）
  - 节点可以复用、替换，不影响其他节点
  - 流程可视化（LangGraph Studio 可直接渲染图结构）
- 什么时候值得上 graph：流程超过 3 步、需要条件分支、需要暂停/恢复、需要多轮会话记忆。

**Phase 1 验收**：

- 执行路径：`check_stock → (route) → calc_price → apply_discount → accept_order → END`，库存不足时走 `reject_order → END`。
- 为什么用 graph 而不是函数：函数解决"能不能跑通"，graph 解决"跑通之后能不能暂停、恢复、调试、替换节点"。

卡点：无。

下一步（Phase 2）：

- 配置 `.env`（当前示例使用 Anthropic 兼容接口）。
- 用工具调用实现 ReAct 风格循环。

---

## 2026-06-15（环境完善 + 开始 Module 1）

目标：

- 配置好跟做 LangChain Academy 的完整环境。

今日记录：

- `.env` 配置完成，使用 Anthropic 兼容接口（`ANTHROPIC_BASE_URL` + `ANTHROPIC_API_KEY`），`LANGSMITH_TRACING=false`。
- 安装了 `jupyter`、`langchain-anthropic`、`langchain-community`、`langgraph-checkpoint-sqlite` 等全套依赖。
- venv 注册为 Jupyter kernel（名称：`Python (LearnLangGraph)`）。
- LangChain Academy 课程仓库放在 `projects/langchain-academy/`，只读参考，已加入 `.gitignore`。
- 跟做 notebook 时遇到 `ChatOpenAI` 一律换成 `ChatAnthropic(model=os.getenv("MODEL_ID"), base_url=os.getenv("ANTHROPIC_BASE_URL"))`。

下一步：

- 跟做 `projects/langchain-academy/module-1/`，顺序：simple-graph → chain → router → agent → agent-memory。

---

## 2026-06-15（Phase 2 完成）

目标：

- 跟做 module-1，完成 simple-graph → chain → router → agent → agent-memory 全链路。

今日记录：

- `minimal_llm_graph.py`：最小 LLM 图，`MessagesState` 作为 state，单节点调 LLM，理解 messages 字段的追加语义。
- `tool_calling.py`：`bind_tools` 入门——LLM 知道工具存在，可以发出 tool_call，但图在 tool_call 后直接到 END，不执行工具，不循环。
- `chain.py`：两节点串联，`add_system_prompt → call_llm`，体会节点只做一件事的设计原则。
- `router.py`：加入 `ToolNode`，`call_llm → (conditional) → tools → END`。工具执行了，但结果不回 LLM，是单次调用，不是循环。
- `agent.py`：完整 ReAct 循环，`tools → "assistant"` 而非 `tools → END`，使用 `tools_condition` 判断是否继续。LLM 可以多次调工具直到不再需要为止。
- `agent_memory.py`：给 agent 加 `MemorySaver` + `thread_id`，实现跨轮记忆。

关键理解：

- `MessagesState` 内置 `add_messages` reducer，`invoke()` 传入新消息是**追加**，不是覆盖；返回值是整个 thread 的 state 快照。
- router 和 agent 的本质区别：`tools → END`（单次） vs `tools → "assistant"`（循环）。
- `MemorySaver` 把每一轮的完整 state 存成 checkpoint；`thread_id` 是隔离边界，同一 thread 共享历史，不同 thread 互不感知。
- `compile(checkpointer=memory)` 后，每次 `invoke` 都会先从 checkpoint 加载该 thread 的历史 state，执行完再保存新 checkpoint。

**Phase 2 验收**：

- tool call：LLM 发出带参数的工具调用请求，写入 state messages。
- observation：`ToolNode` 执行工具，把结果作为 `ToolMessage` 追加到 state。
- final answer：LLM 读到 ToolMessage，不再发 tool_call，返回最终文本，`tools_condition` 路由到 END。
- 三者都存在 `state["messages"]` 里，按时间顺序追加，checkpointer 持久化整个序列。

卡点：无。

下一步（Phase 3）：

- 自定义 State 字段（不只用 `MessagesState`），设计"学习助教 agent"的短期记忆结构。
- 深入理解 `get_state()`、`get_state_history()`、`update_state()`。
