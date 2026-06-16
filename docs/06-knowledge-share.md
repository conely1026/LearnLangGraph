# 从 if/else 到 LangGraph：我的学习笔记

这是一篇面向分享的学习稿。它不追求覆盖全部 API，而是记录我从“能跑一个流程”到“理解 LangGraph 为什么有用”的主线。

## 一句话理解 LangGraph

LangGraph 是一个有状态的工作流运行时。它让我们把 LLM、工具、条件分支、循环、人工介入和记忆组织成一张可以观察、恢复和调试的图。

如果只是两个函数顺序执行，普通 Python 函数就够了。如果流程开始出现这些情况，LangGraph 的价值会变明显：

- 步骤超过 3 个。
- 中间有条件分支。
- LLM 可能需要反复调用工具。
- 任务需要暂停、恢复或人工审批。
- 需要保存多轮对话和执行历史。
- 以后想观察每一步 state 是怎么变化的。

## 最小心智模型

LangGraph 最重要的三个概念是 `State`、`Node`、`Edge`。

### State

`State` 是整个 graph 运行时携带的数据。它像一份“当前任务进度表”，里面保存输入、中间结果、消息历史、摘要、下一步判断等信息。

### Node

`Node` 是一个执行步骤，通常是一个函数。节点读取 state，返回要更新的字段。

例如：

```python
def classify(state):
    if state["level"] == "beginner":
        return {"next_step": "learn_basic_graph"}
    return {"next_step": "build_agent"}
```

### Edge

`Edge` 决定节点之间怎么流动。普通 edge 是固定路线，conditional edge 会根据 state 动态选择下一步。

典型结构像这样：

```text
classify -> route -> beginner_path -> summarize -> END
                 -> advanced_path -> summarize -> END
```

## 为什么不用普通 if/else？

我一开始最直接的疑问是：这不就是把 if/else 写复杂了吗？

后来用订单处理例子对比后，我的理解变成：

- 普通函数更适合短流程。
- Graph 更适合需要观察、恢复、替换和扩展的长流程。

普通 if/else 能解决“这次能不能跑通”。Graph 进一步解决：

- 每个节点能不能独立测试？
- 中间状态能不能保存？
- 某一步失败后能不能恢复？
- 以后能不能在某个节点前插入人工审批？
- 流程能不能被可视化？

所以 LangGraph 的价值不是让简单代码更短，而是让复杂 agent 流程更可控。

## Tool Calling 到 Agent Loop

LLM 调工具时，通常会经历三种消息：

1. `tool call`：模型说“我要调用某个工具，并给出参数”。
2. `observation`：工具执行后的结果。
3. `final answer`：模型读完工具结果后给出的最终回答。

在 LangGraph 里，这些都存在 `state["messages"]` 里，并按时间顺序追加。

Router 和 Agent 的区别也在这里：

```text
Router:
assistant -> tools -> END

Agent:
assistant -> tools -> assistant -> tools -> assistant -> END
```

Router 是单次工具调用。Agent loop 会在工具执行后回到 LLM，让模型根据 observation 判断是否继续调用工具。

## 记忆怎么理解

我现在把 memory 分成两层：

### 短期记忆：checkpoint

短期记忆关注当前 thread 的连续对话。每次 `invoke()` 后，LangGraph 都可以保存一份 checkpoint。

关键关系：

- `thread_id`：会话隔离边界。
- `checkpoint`：一次执行后的 state 快照。
- `state history`：同一个 thread 的所有 checkpoint 组成的历史。

这适合做多轮对话、任务恢复、time travel 和调试。

### 长期记忆：store

长期记忆关注跨 thread 的信息，比如：

- 用户偏好。
- 项目知识。
- 常用事实。
- 可以语义检索的资料。

这部分更像知识库，需要单独设计 namespace、key、检索方式和更新策略。

## 我目前学到的几个判断

### 不要一开始就上多 agent

很多问题一个清晰的 graph 就够了。先把 state、节点、路由、工具循环、记忆做清楚，再考虑多 agent。

### State 字段要克制

State 不是垃圾桶。字段越多，后面越难判断是谁更新了它、什么时候应该保留、什么时候应该清理。

### 节点尽量只做一件事

一个节点如果又分类、又调用工具、又总结，很快就会失控。拆成小节点之后，路由、测试和调试都会清楚很多。

### 人工介入是 agent 工程里的重要能力

真正接近生产环境后，很多动作不能让模型直接执行，比如发邮件、付款、删文件、发布内容。Human-in-the-loop 不是锦上添花，而是把 agent 放进真实流程的安全边界。

## 当前学习进度

我现在已经完成：

- 最小 graph。
- conditional edge。
- if/else 到 graph 的对照。
- LLM 节点。
- tool calling。
- ReAct agent loop。
- MemorySaver 多轮记忆。
- SqliteSaver 持久化。
- 自定义 State 和摘要记忆。

下一步准备学习 Human-in-the-loop，重点看 interrupt、resume、update_state 和 time travel。

## 最后的学习建议

如果重新开始，我会按这个顺序学：

1. 先写一个完全不接 LLM 的 graph。
2. 用 conditional edge 理解路由。
3. 把一个普通 if/else 流程改成 graph。
4. 再接 LLM。
5. 再接工具。
6. 再做 agent loop。
7. 最后加 checkpoint、memory 和 human-in-the-loop。

这样不会一上来就被 agent、memory、多 agent、RAG 混在一起绕晕。

