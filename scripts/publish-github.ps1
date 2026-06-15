param(
    [ValidateSet("private", "public")]
    [string]$Visibility = "private",

    [string]$Name = "LearnLangGraph",

    [string]$Owner = ""
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    throw "GitHub CLI is not installed or not available in PATH. Install it with: winget install --id GitHub.cli"
}

$insideRepo = git rev-parse --is-inside-work-tree
if ($insideRepo.Trim() -ne "true") {
    throw "Run this script from inside the D:\LearnLangGraph git repository."
}

gh auth status | Out-Host

$repoName = if ($Owner.Trim()) { "$Owner/$Name" } else { $Name }
$visibilityFlag = "--$Visibility"
$args = @("repo", "create", $repoName, "--source", ".", "--remote", "origin", "--push", $visibilityFlag)

Write-Host "Creating GitHub repository: $repoName ($Visibility)"
& gh @args

