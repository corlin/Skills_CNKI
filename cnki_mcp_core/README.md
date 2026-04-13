# CNKI MCP Core (Playwright Async 版)

基于 Playwright 异步引擎构建的中国知网（CNKI）智能能力库内核。

## 🌟 核心特性

- **Playwright 原生异步**：全面迁移至 `async/await` 架构，支持高性能并发处理。
- **海外版优先链路**：深度适配 `oversea.cnki.net`，天然规避国内版 WAF 拦截（如常见的 HTTP 418 报错）。
- **Stealth 隐身加固**：内置动态检测的 Stealth 插件，对抗浏览器指纹识别。
- **Direct URL 协议**：摒弃不稳定的 UI 模拟点击，采用直接构造 URL 参数的方式启动检索。

## 🛠️ 安装环境

本项目使用 `uv` 进行包管理：

```bash
# 同步依赖
uv sync

# 安装 Playwright 浏览器内核
uv run playwright install chromium
```

## 🚀 快速验证

我们提供了一个全链路验证脚本，可一次性测试搜索、详情解析功能：

```bash
uv run python verify_cnki.py
```

## 🔧 配置项 (环境变量)

| 变量名 | 说明 | 默认值 |
| :--- | :--- | :--- |
| `CNKI_HEADLESS` | 是否以无头模式运行浏览器 | `true` |
| `CNKI_DIRECT` | 是否强制使用直连模式 | `true` |

## 🏗️ 架构说明

- **`core/browser_pw.py`**: 异步浏览器上下文管理器，负责 Cookie 持久化和隐身配置。
- **`services/search_service.py`**: 核心检索服务，负责处理复杂的检索词构造和结果解析。
- **`services/detail_service.py`**: 详情页解析引擎，提取 DOI、摘要及关键词。
- **`main.py`**: 基于 FastMCP 的主入口，提供标准化的智能能力接口。

---
*Powered by Antigravity*
