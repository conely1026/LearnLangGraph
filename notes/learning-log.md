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
