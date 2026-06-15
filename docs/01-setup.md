# 环境安装

## Python 环境

建议使用 Python 3.11 或 3.12。当前机器上可以用 `py -3.11` 直接创建更稳的学习环境。

```powershell
cd D:\LearnLangGraph
py -3.11 --version
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -U pip
pip install -r requirements.txt
```

验证：

```powershell
python src\hello_graph.py
```

## API Key

`src/hello_graph.py` 不需要 API Key。后续 LLM 示例需要复制环境文件：

```powershell
Copy-Item .env.example .env
notepad .env
```

至少需要：

```text
OPENAI_API_KEY=你的 key
```

LangSmith 是可选的，但建议学习中期开启，用来观察 graph 的执行过程。

## 推荐编辑器

- VS Code
- Cursor
- PyCharm

建议安装 Python、Jupyter、Markdown Preview 插件。

## 常见问题

### PowerShell 不允许激活虚拟环境

可以临时放开当前用户脚本策略：

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### pip 安装慢

先确认网络正常，再考虑使用公司或学校网络代理。不要把代理、token 或 API key 写进仓库。
