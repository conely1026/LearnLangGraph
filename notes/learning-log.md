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

---

## 2026-06-16（Module-2 State & Memory 概念梳理）

目标：

- 跟读 module-2 notebook，理解 state schema、reducer、multiple schemas、memory 架构。

今日记录：

**State Schema 三种写法：**
- `TypedDict`：纯静态类型提示，无默认值，无运行时校验，学习/原型首选。
- `@dataclass`：支持 `field(default_factory=...)` 默认值，字段多时减少 invoke 传参负担；裸写 `list = []` 会共享同一对象（等价 C++ static 成员），必须用 `field(default_factory=list)`。
- `Pydantic BaseModel`：运行时强校验类型，生产环境防御用。

**Reducer：**
- 无 `Annotated` → 节点返回值直接覆盖字段。
- `Annotated[list, add_messages]` → 追加，同 id 的消息替换而非追加。
- `Annotated[list, 自定义函数]` → 自定义合并逻辑。
- `add_messages` 实现：两端都 coerce 成 list，无 id 的消息自动补 UUID，用 dict 做 O(1) id 查重，`RemoveMessage` 可删除指定消息，`REMOVE_ALL_MESSAGES` 清空历史。
- `None` 不做守卫，由外层 `_add_messages` 拦截；正常用法不会传 None。

**Multiple Schemas：**
- `PrivateState`：只在特定节点间流转的中间字段，不进 `OverallState`，执行完自动消失。
- `input_schema` / `output_schema`：在 `StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)` 处声明，对图的入口和出口做字段过滤，内部节点仍用完整 `OverallState`。

**Memory 两层架构：**
- 短期（checkpointer）：state 快照按 `thread_id + checkpoint_id` 存储，同 thread invoke 直接取最新，key-value 查找，无检索。
- 长期（store）：按 `namespace + key` 存储，支持精确查找和语义检索（向量化相似度搜索），跨 thread 持久化，适合存用户偏好、知识库。

卡点：无。

下一步：

- 继续 module-2 剩余内容（trim_messages、长期记忆 store）。
- Phase 3 收尾：写 `learning_assistant.py`，自定义 State + MemorySaver。

---

## 2026-06-16（Module-2 收尾：消息管理 + 持久化）

目标：

- 跟读 module-2 剩余三章：trim-filter-messages、chatbot-summarization、chatbot-external-memory。

今日记录：

**消息管理三种策略（trim-filter-messages）：**
- `RemoveMessage`：改 State 本身，物理删除旧消息，适合真的不需要保留历史。
- 切片 `messages[-n:]`：不改 State，传给 LLM 时截断，按条数控制，粗糙。
- `trim_messages`：不改 State，按 token 数裁剪，`strategy="last"` 保留最新，精度更高。
- 三者都是"原语"，实际按场景选：实时战斗 AI 用 trim，NPC 对话记忆用 summarization。

**摘要记忆（chatbot-summarization）：**
- State 扩展 `summary: str` 字段，存压缩后的旧对话。
- `call_model`：有摘要时作为 SystemMessage 前置，LLM 收到"摘要 + 最近消息"。
- `summarize_conversation`：messages + "请总结" 发给 LLM，结果写入 `summary`，然后 `RemoveMessage` 只留最后 2 条。
- 摘要是续写不是重写，`should_continue` 超 6 条才触发，配合 MemorySaver 跨轮持久。

**外部持久化（chatbot-external-memory）：**
- 把 `MemorySaver` 换成 `SqliteSaver(conn)`，图逻辑一行不改。
- Checkpointer 可插拔：MemorySaver → SqliteSaver → PostgresSaver，上层无感知。
- 对应游戏存档：每个玩家 thread_id 是存档 ID，切换 checkpointer 不改 agent 代码。

**Module-2 全部完成**：6 个 notebook 跟读完毕。

卡点：无。

下一步：

- Phase 3 收尾：写 `src/phase-3/learning_assistant.py`，自定义 State + MemorySaver。
- 跟读 Module-3：Human-in-the-loop（breakpoints、edit-state、time-travel）。

---

## 2026-06-16（Phase 3 完成：learning_assistant.py）

目标：

- 实现 `src/phase-3/learning_assistant.py`，整合自定义 State、摘要记忆、SqliteSaver 持久化。

今日记录：

**自定义 State：**
- `LearningState` 继承 `MessagesState`，扩展 `topic`、`level`、`summary` 三个字段。
- `topic/level` 通过 `graph.update_state()` 在首次启动时写入，后续从 checkpoint 读取，不用每轮传递。

**节点实现：**
- `call_model`：把 topic/level/summary 拼成 system prompt，summary 追加在角色定位之后而非单独一条 SystemMessage。
- `summarize_conversation`：首次生成/续写摘要，删旧消息只留最后 2 条。

**持久化：**
- 用 `SqliteSaver` 替换 `MemorySaver`，db 固定在项目根目录 `state_db/learning_assistant.db`，用 `__file__` 定位路径，不依赖运行时工作目录。
- 同一个 db 可存多个 thread，靠 `thread_id` 隔离，对应游戏多玩家存档场景。

**config 传递规律：**
- 凡是和持久化 state 交互的操作都要传 config：`invoke`、`get_state`、`update_state`、`stream`、`get_state_history`。

**Phase 3 验收：**
- 能解释 thread_id / checkpoint / state snapshot 三者关系：thread_id 是隔离边界，每次 invoke 生成一个 checkpoint（state 快照），同 thread 的所有 checkpoint 构成完整历史。

**下一步：**
- Module-3：Human-in-the-loop（breakpoints、edit-state、time-travel）。

---

## 2026-06-16（Phase 4 进行中：Human-in-the-loop + 人设项目 + 流式）

目标：

- 跟读 Module-3 的 breakpoints / edit-state-human-feedback / streaming，并落两个练习。

今日记录：

- `src/phase-4/human_review.py`：审批 agent。`compile(interrupt_before=["tools"])` 在调工具前中断，支持 approve / edit / reject 三条路径。
- `src/phase-4/su_shi.py`：历史人物（苏轼）人设 agent。`classify` 节点判意图写入 `state["intent"]`，conditional edge 分流到 quote（引用真迹）/ create（即兴代拟）/ chat（闲谈）三个节点，各用不同系统提示。后改成流式聊天。

关键理解：

- **interrupt + resume**：断点本质是把当前 state 存成 checkpoint 再 return；用 `graph.stream(None, thread)` 从该 checkpoint 续跑（input 传 `None` = 不加新输入，从 `state.next` 继续）。所以中断前后 state 从没丢，只是执行流被挂起。必须配 checkpointer。
- **看/改中断点**：`get_state(thread).next` 非空即被中断；`update_state(thread, {...})` 改 state，`messages` 字段走 `add_messages` reducer（无 id 追加 / 带 id 覆盖）；`as_node="X"` 可把更新假装成某节点的输出。
- **创作 vs 引用边界**：人设 agent 必须区分「即兴代拟」和「引用真迹」，前者强制标注非真迹，后者不确定就坦白、绝不编造。逐字引用准确性留给 Phase 5 RAG。
- **streaming 三模式**：`values`（每节点后完整 state）/ `updates`（增量更新）/ `messages`（节点内 LLM 逐 token，给 `(chunk, metadata)`）。组合 `stream_mode=["updates","messages"]` 可同时拿状态和 token。
- **token 过滤靠 `metadata["langgraph_node"]`**：多节点图里每个调 LLM 的节点都会吐 token，su_shi 的 classify 节点也会流出「引用/创作/闲聊」标签 token，必须按 langgraph_node 只放行回答节点。教材的等价异步写法是 `astream_events(version="v2")` 过滤 `on_chat_model_stream`。

卡点：

- `get_state_history()` 如何用于 time-travel 回放，还没动手。
- 多个 tool_call 同时出现时，reject 分支只补了第一个 ToolMessage（已在代码里标注为练习点）。

下一步：

- 收尾 Module-3：跟读 `time-travel`，用 `get_state_history()` 回到历史 checkpoint 重跑。
- 之后 Phase 5：把 `su_shi.py` 升级成 RAG 版，解决逐字引用准确性。
