# 可跟做资源清单

这里优先收集官方、维护活跃、代码完整的资源。

## 官方主线

### LangGraph 官方文档

地址：https://docs.langchain.com/oss/python/langgraph/overview

用途：

- 查概念
- 查 API
- 对照当前版本

建议先读 Overview、Quickstart、Concepts，再读 Persistence、Human-in-the-loop、Memory。

### LangChain Academy - Introduction to LangGraph

地址：https://academy.langchain.com/courses/intro-to-langgraph

本地路径：`projects/langchain-academy/`

跟做顺序（module-1）：

```
simple-graph.ipynb
chain.ipynb
router.ipynb
agent.ipynb
agent-memory.ipynb
```

注意：notebook 里用 `ChatOpenAI`，跟做时替换为：

```python
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model=os.getenv("MODEL_ID"), base_url=os.getenv("ANTHROPIC_BASE_URL"))
```

### LangGraph 101

地址：https://github.com/langchain-ai/langgraph-101

用途：

- 适合第二遍跟做
- 覆盖 101 和 201
- 包含 human-in-the-loop、multi-agent、research agent、DeepAgents

## 课程

### DeepLearning.AI - AI Agents in LangGraph

地址：https://www.deeplearning.ai/courses/ai-agents-in-langgraph

用途：

- 用课程节奏理解 agent loop
- 适合已经跑通过基础 graph 之后学习

### DeepLearning.AI - Long-Term Agentic Memory With LangGraph

地址：https://www.deeplearning.ai/courses/long-term-agentic-memory-with-langgraph

用途：

- 专门补 memory 设计
- 适合做个人助理、邮件助理、知识库助理时学习

### Hugging Face Agents Course - LangGraph Unit

地址：https://huggingface.co/learn/agents-course/en/unit2/langgraph/introduction

用途：

- 横向理解 agent 框架
- 不作为主线，但适合补充视角

## 官方模板和项目

### new-langgraph-project

地址：https://github.com/langchain-ai/new-langgraph-project

用途：

- 学 LangGraph Server / Studio 项目结构
- 适合第 7 阶段

### react-agent

地址：https://github.com/langchain-ai/react-agent

用途：

- 学 ReAct 工具调用循环
- 适合第 2 阶段

### retrieval-agent-template

地址：https://github.com/langchain-ai/retrieval-agent-template

用途：

- 学 RAG agent
- 适合第 5 阶段

### rag-research-agent-template

地址：https://github.com/langchain-ai/rag-research-agent-template

用途：

- 学研究型 RAG 和 researcher subgraph
- 适合第 5-6 阶段

### open_deep_research

地址：https://github.com/langchain-ai/open_deep_research

用途：

- 进阶真实项目
- 适合学习 deep research agent、评测、工具组合和多模型配置

