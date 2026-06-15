# LangGraph 学习路线图

这份路线按“先能跑，再理解，再做项目”的顺序设计。建议每天 45-90 分钟，完整走完约 4 周。

## 第 0 阶段：环境与最小图

目标：先跑通一个不依赖模型的 LangGraph。

任务：

- 阅读 `README.md` 的快速开始。
- 运行 `python src\hello_graph.py`。
- 修改 `level` 字段，观察输出变化。
- 用自己的话写下：State 是什么，Node 是什么，Edge 是什么。

验收：

- 能解释一次 `invoke()` 过程中 state 如何被节点修改。

## 第 1 阶段：基础图模型

目标：掌握 StateGraph 的基本形态。

跟做资源：

- LangChain Academy - Introduction to LangGraph
- LangGraph 官方文档 Overview / Concepts
- `langchain-ai/langgraph-101` 的 101 部分

任务：

- 写一个三节点 graph：输入分类、处理、总结。
- 写一个 conditional edge：根据用户意图走不同节点。
- 尝试把一个普通 if/else 脚本改成 graph。

验收：

- 能画出自己的 graph 执行路径。
- 能说清楚“为什么这里需要 graph，而不是一个普通函数”。

## 第 2 阶段：LLM 与工具调用

目标：理解 agent loop。

跟做资源：

- 官方 `react-agent` 模板
- DeepLearning.AI - AI Agents in LangGraph

任务：

- 配置 `.env`。
- 用一个搜索或计算工具实现 ReAct 风格循环。
- 记录 agent 什么时候应该继续调用工具，什么时候应该结束。

验收：

- 能解释 tool call、observation、final answer 如何被 state 串起来。

## 第 3 阶段：持久化、检查点和记忆

目标：让 graph 可以恢复、追踪和跨轮对话。

任务：

- 给 graph 接入 checkpointer。
- 对比无 memory 和有 memory 的多轮结果。
- 设计一个“学习助教 agent”的短期记忆字段。

验收：

- 能解释 thread id、checkpoint、state snapshot 的关系。

## 第 4 阶段：Human-in-the-loop

目标：让关键步骤可以被人暂停、审核和改写。

任务：

- 在 graph 中加入一个审批节点。
- 在生成正式答案前中断，手动修改 state。
- 记录适合人工介入的场景：付款、发邮件、删文件、发布内容。

验收：

- 能说清楚 interrupt 前后的状态如何恢复。

## 第 5 阶段：RAG / Research Agent

目标：做一个真实可用的小项目。

推荐项目：

- 资料检索学习助手
- 论文阅读助手
- 代码库问答助手

跟做资源：

- 官方 `retrieval-agent-template`
- 官方 `rag-research-agent-template`
- `open_deep_research`

验收：

- 能完成“检索资料 -> 归纳引用 -> 生成结构化答案”的闭环。

## 第 6 阶段：多 agent 与子图

目标：把复杂任务拆成多个角色。

任务：

- 拆分 planner、researcher、writer、critic。
- 用 subgraph 或 supervisor 控制协作。
- 对比单 agent 和多 agent 的成本、延迟、稳定性。

验收：

- 能判断什么时候不该上多 agent。

## 第 7 阶段：部署、调试与评测

目标：从 notebook 走向可运行服务。

任务：

- 跑官方 `new-langgraph-project`。
- 用 LangGraph Studio 观察 graph。
- 设计 10 条固定测试样例，记录失败模式。

验收：

- 能把一个 LangGraph 项目从本地脚本整理成可调试服务。

