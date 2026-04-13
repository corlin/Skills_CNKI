# Skills_CNKI: 中国知网 (CNKI) 智能学术助手能力库

[![Model Context Protocol](https://img.shields.io/badge/MCP-Standard-orange)](https://modelcontextprotocol.io/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://github.com/astral-sh/uv)

本项目致力于通过 **Model Context Protocol (MCP)** 协议，为 AI 助手（如 Cursor, Claude Desktop, Windsurf）构建一套全面、稳健且合规的中国知网（CNKI）学术研究能力体系。

## ✨ 核心能力

-   **🔍 智能文献检索**：多维度（主题、关键词、作者、DOI）精准检索知网文献，获取高质量元数据。
    -   *推荐工具*：`h-lu/cnki-mcp`
-   **✅ 引文真实性核验**：自动化验证 AI 产生的学术引用，彻底消除“学术幻觉”。
    -   *推荐工具*：`buluo533/CNKI-MCP-Verifier`
-   **联盟聚合搜索**：一键打通 CNKI 与 arXiv, Semantic Scholar, Google Scholar 等全球学术资源。
    -   *推荐工具*：`h-lu/paper-find-mcp`
-   **🔗 官方 API 集成**：提供基于 `uv` 管理的 Python 封装框架，支持知网 OpenX 官方接口与 JWT 认证。
-   **🤖 自动化科研工作流**：支持期刊追踪、PDF 下载及文献自动导入 Zotero。

## 📁 目录结构

```text
.
├── documentation/          # 深度调研报告与使用指南
│   ├── cnki_mcp_guide.md  # 主中心集成指南 (必读)
│   └── refprj.md          # 社区 9 个相关开源项目深度分析
├── mcp_configs/            # MCP 服务器配置模板 (.json)
├── scripts/
│   └── cnki_api_wrapper/   # 基于 uv 的官方 API 封装 Python 项目
└── cnki_skill_definition.md # AI 助手统一技能调度定义
```

## 🚀 快速开始

### 1. 配置 MCP 服务器
将 `mcp_configs/cnki_unified_config.json` 中的各组件配置复制到您的 IDE (Cursor/Windsurf) 或 Claude Desktop 配置文件中。

### 2. 使用官方 API 封装
```bash
cd scripts/cnki_api_wrapper
uv sync
```

### 3. 指令模式参考
在 AI 对话中尝试：
- *“帮我搜索关于 [量子计算] 的最新核心期刊论文，并核实结果的真实性。”*
- *“根据这篇论文的 DOI，获取其详细摘要并导出到 Zotero。”*

## 📚 参考项目
本项目在开发过程中深度参考并致敬了以下优秀开源项目：
- `h-lu/cnki-mcp`
- `cookjohn/cnki-skills`
- `MagicCNKI`
- `yang-kun-long/library-access-mcp`

更多项目详情请参阅 [Reference Projects](documentation/refprj.md)。

## ⚠️ 法律与免责声明
本项目及其提供的配置方案仅用于学术研究与合规的数据检索。请务必遵守《中国知网用户服务协议》以及国家相关法律法规。**严禁利用此类工具进行大规模非法数据抓取或商业化分发。**

## 🤝 贡献与反馈
欢迎在 GitHub 提交 Issue 或 Pull Request 以完善本项目。

---
Produced by Antigravity AI.
