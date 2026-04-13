# CNKI MCP & Skill 集成使用指南

本指南将协助您在本地环境中启用并高效使用中国知网 (CNKI) 相关的 MCP 扩展和自动化技能。

## 1. 快速配置 MCP 服务器 (Cursor / Claude Desktop)

请将以下内容合并到您的 MCP 配置文件中（通常位于 `~/.codeium/mcp.json` 或 `~/Library/Application Support/Claude/claude_desktop_config.json`）：

### 推荐配置模板
```json
{
  "mcpServers": {
    "cnki-standard": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/h-lu/cnki-mcp", "cnki-mcp"]
    },
    "cnki-verifier": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/buluo533/CNKI-MCP-Verifier", "cnki-mcp-verifier"]
    },
    "paper-find": {
      "command": "uvx",
      "args": ["--from", "git+https://github.com/h-lu/paper-find-mcp", "paper-find-mcp"]
    }
  }
}
```

---

## 2. 官方 OpenX API 封装使用 (基于 uv)

在 `scripts/cnki_api_wrapper/` 下已为您备好符合 `uv` 管理标准的 Python 项目。

### 获取凭据
1. 访问 [知网研学开放平台](https://openx.cnki.net/) 申请 AppId, ApiKey 和 SecretKey。
2. 在 `auth.py` 中填入您的凭据。

### 运行环境准备
```bash
cd scripts/cnki_api_wrapper
uv sync
```

---

## 3. Chrome DevTools 自动化技能 (Advanced Search)

对于极其复杂的“高级检索”或需要“下载 PDF 到本地”的场景，建议结合 `chrome-devtools` MCP 使用。

### 操作流程
1. 运行 `npx @modelcontextprotocol/server-chrome-devtools` 连接浏览器。
2. 指挥 AI：“帮我打开知网高级检索页面，设置主题为‘深度学习’，时间为 2024 年至今，执行检索并将结果导出到我的文献库。”

---

## 4. 最佳实践推荐 (The Workflow)

> [!IMPORTANT]
> **防止被封禁**：知网对自动化频率非常敏感。**请务必不要编写死循环爬虫**。AI 助手每次调用应有明确的目标。
> **双重验证**：在生成任何学术引用前，强力建议调用 `cnki-verifier` 进行真实性校验。

---

## 5. 项目参考
详细的参考项目分析见：[documentation/refprj.md](file:///Users/corlin/2026/Skill_CNKI/documentation/refprj.md)
本项目远程地址：[https://github.com/corlin/Skills_CNKI](https://github.com/corlin/Skills_CNKI)
