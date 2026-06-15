# 发布到 GitHub

本机当前没有检测到 GitHub CLI，所以远端仓库需要先安装并登录 `gh`。

## 1. 安装 GitHub CLI

Windows 推荐：

```powershell
winget install --id GitHub.cli
```

安装后重新打开 PowerShell，确认：

```powershell
gh --version
```

## 2. 登录 GitHub

```powershell
gh auth login
gh auth status
```

建议选择：

- GitHub.com
- HTTPS
- Login with a web browser

## 3. 创建远端仓库并推送

默认创建私有仓库：

```powershell
cd D:\LearnLangGraph
.\scripts\publish-github.ps1
```

创建公开仓库：

```powershell
cd D:\LearnLangGraph
.\scripts\publish-github.ps1 -Visibility public
```

指定仓库名：

```powershell
.\scripts\publish-github.ps1 -Name LearnLangGraph
```

脚本会执行：

- 检查当前目录是否是 git 仓库
- 检查 GitHub CLI 是否可用
- 检查 GitHub 登录状态
- 创建 GitHub 仓库
- 设置 `origin`
- 推送 `main`

