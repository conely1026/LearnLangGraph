# Learn LangGraph

这是一个面向自学和跟做的 LangGraph 学习仓库。目标不是收藏链接，而是用一条可执行路径把 LangGraph 的核心能力学起来：图状态、节点、路由、循环、工具调用、持久化、人类介入、RAG 和多 agent。

## 学习目标

完成本仓库后，你应该能够：

- 解释 LangGraph 的 `State`、`Node`、`Edge`、`Conditional Edge`、`Checkpoint` 和 `Memory`。
- 写出一个可以循环、分支、重试的 agent graph。
- 把 LLM、工具调用、检索和人工审批接入同一个状态图。
- 用 LangGraph Studio / LangSmith 观察执行路径和调试状态。
- 从官方模板改出自己的研究助手或 RAG agent。

## 推荐学习路径

| 阶段 | 主题 | 产出 |
| --- | --- | --- |
| 0 | 环境与心智模型 | 跑通 `src/hello_graph.py` |
| 1 | StateGraph 基础 | 自己实现一个分支工作流 |
| 2 | LLM + Tool Calling | 实现一个 ReAct 风格工具 agent |
| 3 | Persistence / Memory | 加入 checkpoint 和会话记忆 |
| 4 | Human-in-the-loop | 在关键节点加入人工审批 |
| 5 | RAG / Research Agent | 做一个可检索资料的研究助手 |
| 6 | 多 agent / 子图 | 拆分 planner、researcher、writer |
| 7 | 部署与评测 | 用 LangGraph Server / Studio 跑项目 |

详细路线见 [docs/00-learning-roadmap.md](docs/00-learning-roadmap.md)。

## 本地快速开始

```powershell
cd D:\LearnLangGraph
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
python src\hello_graph.py
```

`src/hello_graph.py` 不需要 API Key，先用纯 Python 节点理解图的执行方式。

本机默认 `python` 可能指向更新版本。LangGraph 学习阶段建议优先使用 Python 3.11 或 3.12。

如果后面要接入 Anthropic 兼容模型或其他模型：

```powershell
Copy-Item .env.example .env
notepad .env
```

## 仓库结构

```text
D:\LearnLangGraph
├── README.md
├── requirements.txt
├── .env.example
├── docs
│   ├── 00-learning-roadmap.md
│   ├── 01-setup.md
│   ├── 02-core-concepts.md
│   ├── 03-follow-along-resources.md
│   └── 04-project-ideas.md
├── src
│   └── hello_graph.py
├── projects
│   └── README.md
└── notes
    └── learning-log.md
```

## 高质量跟做资源

- LangGraph 官方文档: https://docs.langchain.com/oss/python/langgraph/overview
- LangChain Academy - Introduction to LangGraph: https://academy.langchain.com/courses/intro-to-langgraph
- 官方课程代码仓库: https://github.com/langchain-ai/langchain-academy
- LangGraph 101: https://github.com/langchain-ai/langgraph-101
- DeepLearning.AI - AI Agents in LangGraph: https://www.deeplearning.ai/courses/ai-agents-in-langgraph
- 官方模板 new-langgraph-project: https://github.com/langchain-ai/new-langgraph-project
- 官方模板 react-agent: https://github.com/langchain-ai/react-agent
- 官方项目 open_deep_research: https://github.com/langchain-ai/open_deep_research

## 学习记录与分享

- 阶段学习记录：[notes/learning-record.md](notes/learning-record.md)
- 每日学习日志：[notes/learning-log.md](notes/learning-log.md)
- 可分享知识稿：[docs/06-knowledge-share.md](docs/06-knowledge-share.md)

## 第一周建议

1. 跑通本仓库的最小 graph。
2. 完成 LangChain Academy Introduction to LangGraph 的 module 0-2。
3. 把课程里的 router 示例用自己的业务问题重写一遍。
4. 在 `notes/learning-log.md` 记录每天卡住的概念和解决方式。

## 发布到 GitHub

本机当前没有可用的 GitHub CLI。安装并登录后，执行：

```powershell
cd D:\LearnLangGraph
.\scripts\publish-github.ps1
```

详细说明见 [docs/05-publish-to-github.md](docs/05-publish-to-github.md)。
