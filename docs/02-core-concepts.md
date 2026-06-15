# LangGraph 核心概念

## State

State 是 graph 运行时携带的共享数据。每个节点读取 state，并返回对 state 的更新。

你可以把它理解成“工作流当前进度 + 中间结果 + 下一步需要的信息”。

## Node

Node 是一个可执行步骤，通常是一个函数。

常见节点：

- 调用 LLM
- 调用工具
- 检索资料
- 判断是否需要继续
- 生成最终回答
- 等待人工审批

## Edge

Edge 决定节点之间的流向。

普通 edge 是固定流向；conditional edge 会根据 state 动态选择下一步。

## Conditional Edge

Conditional edge 是 LangGraph 很重要的能力。它让 agent 可以根据执行结果决定：

- 继续调用工具
- 进入人工审批
- 重试
- 结束
- 交给另一个 agent

## Checkpoint

Checkpoint 保存 graph 的中间状态。它让长任务可以恢复，也让多轮会话可以沿着同一条 thread 继续。

## Memory

Memory 是建立在持久化和 state 设计上的能力。短期 memory 通常在当前 thread 内有效，长期 memory 通常需要额外的存储和检索设计。

## Human-in-the-loop

Human-in-the-loop 让 graph 在关键节点暂停，等待人类确认或修改 state。适合高风险动作，比如发邮件、付款、发布内容、删除文件。

## Subgraph

Subgraph 用来把复杂流程拆成可复用的小图。多 agent 系统里常用 subgraph 表达不同角色或不同阶段。

