# Projects

## langchain-academy（跟做参考）

`projects/langchain-academy/` 是 LangChain Academy 官方课程仓库的本地副本，只读参考用，不纳入本仓库 git 追踪。

跟做顺序：

```
module-1/simple-graph.ipynb
module-1/chain.ipynb
module-1/router.ipynb
module-1/agent.ipynb
module-1/agent-memory.ipynb
```

注意：notebook 里用 `ChatOpenAI`，跟做时换成：

```python
from langchain_anthropic import ChatAnthropic
llm = ChatAnthropic(model=os.getenv("MODEL_ID"), base_url=os.getenv("ANTHROPIC_BASE_URL"))
```

---

## 自建项目（后续阶段）

这里放每个阶段完成后的自建项目，建议一个项目一个目录：

```text
projects/
├── langchain-academy/     ← 跟做参考（只读）
├── 01-learning-coach/
├── 02-rag-assistant/
├── 03-human-approval-email/
├── 04-codebase-qa/
└── 05-deep-research-mini/
```

每个自建项目建议包含：

- `README.md`：项目目标和运行方法
- `src/`：代码
- `notes.md`：学习记录和失败模式

