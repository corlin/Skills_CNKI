# Skill_CNKI: 中国知网集成科研基础设施 (Modular V2)

这是一个基于 MCP (Model Context Protocol) 协议构建的专业级知网科研工具集。本项目通过吸收 `cnki-mcp`, `CNKI-skills`, `library-access-mcp`, 和 `GeoSchlor-MCP` 等社区优秀项目的底层逻辑，为您提供一站式的学术辅助能力。

## 📁 项目模块化结构

为了保证高性能与易维护性，系统采用了模块化架构：

-   **`core/`** (地中海核心):
    -   `browser.py`: 高级浏览器池管理，自动处理 Cookie 持久化与反爬策略。
    -   `constants.py`: 知网字段映射、排序选项等静态配置。
    -   `utils.py`: 相似度计算、RIS 导出、安全文件名处理。
-   **`services/`** (学术服务层):
    -   `search_service.py`: 协议级精准搜索逻辑。
    -   `detail_service.py`: 深度详情解析与元数据提取。
    -   `download_service.py`: 自动化安全下载流程与交互登录。
-   **`main.py`**: 服务统一入口。

## 🌟 核心工具集

| 工具 | 核心逻辑来源 | 主要功能 |
| :--- | :--- | :--- |
| `search_cnki` | GeoSchlor-MCP | 协议级极速检索，支持多种过滤条件 |
| `get_paper_detail` | cnki-mcp | 提取完整摘要、关键词、被引与 DOI |
| `verify_paper` | CNKI-Verifier | 抗幻觉核验，检测引文真实性 |
| `interactive_login` | Library-Bridge | 弹出窗口辅助登录机构/校园网 |
| `download_paper` | CNKI-skills | 执行具有安全时延的自动化下载 |
| `export_to_zotero` | Custom Logic | 一键生成 .ris 元数据，无缝导入 Zotero |

## 🚀 快速开始

### 1. 安装依赖
```bash
cd cnki_mcp_core
uv sync
```

### 2. 连接 MCP 服务
将 `mcp_configs/cnki_unified_config.json` 中的配置内容复制并贴入您的 Cursor 或 Claude Desktop 配置文件。

### 3. 连接状态检查
启动服务后，首先运行 `check_status` 工具。如果提示需要权限，运行 `interactive_login` 并根据提示在弹出的窗口中登录您的机构账号。

## 🛡️ 安全提示
本项目遵循 **CNKI-skills 六大安全原则**：
- 默认执行 5-7 秒随机延迟。
- 禁止任何破坏、攻击知网系统的行为。
- 文件默认保存至 `downloads/` 目录。
