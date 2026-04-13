# CNKI 相关项目参考指南 (Reference Projects)

本指南汇总了目前社区中与知网 (CNKI) 及学术搜索相关的 Model Context Protocol (MCP) 服务器和技能集 (Skills) 项目。

---

## 🚀 核心搜索与标准 MCP 实现 (Core Search)

### 1. [cnki-mcp (h-lu)](https://github.com/h-lu/cnki-mcp)
- **定位**：专业级知网检索 MCP 服务器。
- **核心功能**：支持按主题、关键词、作者搜索，获取论文摘要、DOI 等。
- **技术栈**：Python, FastMCP, Playwright。
- **推荐理由**：目前社区中最稳定、配置最标准的知网 MCP 插件，完美适配 Cursor 和 Claude Desktop。

### 2. [paper-find-mcp (h-lu)](https://github.com/h-lu/paper-find-mcp)
- **定位**：中英文多源学术检索聚合器。
- **核心功能**：一键搜索 CNKI, arXiv, Semantic Scholar, PubMed, Google Scholar 等。
- **技术栈**：Python, FastMCP。
- **推荐理由**：适合进行中英文文献对比研究，提供全局学术视野。

---

## 🛠️ 工作流与深度技能集成 (Integrated Skills)

### 3. [cnki-skills (cookjohn)](https://github.com/cookjohn/cnki-skills)
- **定位**：针对 Claude Code 的知网全功能技能包。
- **核心功能**：搜索、期刊浏览、**PDF 自动下载**、通过 Chrome DevTools **导出到 Zotero**。
- **推荐理由**：目前功能最全面的工作流集成方案，适合重度科研管理。

### 4. [CNKI-skills (lbnqq)](https://github.com/lbnqq/CNKI-skills)
- **定位**：类似于 cookjohn 的技能实现，侧重于特定交互场景的优化。

---

## 🧪 真实性验证与反幻觉 (Verification)

### 5. [CNKI-MCP-Verifier (buluo533)](https://github.com/buluo533/CNKI-MCP-Verifier)
- **定位**：学术引用真实性验证工具。
- **核心功能**：AI 引用文献前自动查询知网，对比标题和作者，判断论文是否真实存在。
- **推荐理由**：**科研场景必备**，有效防止 AI 产生虚假引用的“幻觉”。

---

## 🔐 认证、接入与自动化 (Access & Automation)

### 6. [library-access-mcp (yang-kun-long)](https://github.com/yang-kun-long/library-access-mcp)
- **定位**：通过浏览器插件桥接实现学术数据库访问。
- **核心功能**：利用用户已有的 IEEE, Springer, CNKI 等机构认证 session，规避反爬风险。
- **推荐理由**：**校园网/VPN 用户核心方案**，解决自动化工具难以通过机构认证的痛点。

---

## 📐 特定领域与定制化 (Domain Specific)

### 7. [GeoSchlor-MCP (luskB)](https://github.com/luskB/GeoSchlor-MCP)
- **定位**：地质学与物探测井方向定制检索。
- **亮点**：支持特定学科的数据源聚合（GEOPHYSICS, OnePetro 等）及搜索后处理。

### 8. [cnki-journal-fetcher (xulei-shl)](https://github.com/xulei-shl/cnki-journal-fetcher)
- **定位**：CNKI 期刊论文追踪助手。
- **核心功能**：定期获取特定核心期刊的最新发表论文列表。

---

## 📚 底层逻辑与 API 参考 (Logic Reference)

### 9. [MagicCNKI (1049451037)](https://github.com/1049451037/MagicCNKI)
- **定位**：知网搜索 API 封装库（MagicBaidu 兄弟项目）。
- **价值**：提供了最扎实的底层搜索逻辑参考，是手动编写高自定义爬虫技能时的最佳代码库。

---

> [!TIP]
> **使用建议**：建议优先部署 `h-lu/cnki-mcp` 作为基础搜索能力，配合 `buluo533/CNKI-MCP-Verifier` 进行抗幻觉验证，并在下载环节参考 `yang-kun-long` 的浏览器桥接思路。