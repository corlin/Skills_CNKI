# CNKI 综合技能定义 (Skill Definition)

本技能集定义了 AI 助手如何高效利用中国知网 (CNKI) 相关工具进行学术研究。

## 🛠️ 工具箱矩阵

### 1. 深度检索与基本细节 (Standard Search)
- **核心工具**：`cnki-standard` (h-lu/cnki-mcp)
- **使用场景**：当需要查找特定主题、作者或 DOI 的论文详情（摘要、出版日期等）时。

### 2. 真实性验证 (Verifier)
- **核心工具**：`cnki-verifier` (buluo533/CNKI-MCP-Verifier)
- **使用场景**：在撰写学术报告或列出参考文献前，**务必调用**以确保提到的论文在知网确实存在，防止 AI 幻觉。

### 3. 多源学术聚合 (Global Research)
- **核心工具**：`paper-find` (h-lu/paper-find-mcp)
- **使用场景**：需要查找中英文对比文献，或知网结果较少需要扩充到 arXiv/Google Scholar 时。

### 4. 自动化下载与管理 (Workflow)
- **核心工具**：`chrome-devtools` + `cookjohn/cnki-skills` 逻辑
- **使用场景**：需要批量浏览期刊目录、下载 PDF 全文或将其导出至 Zotero 库。

---

## 🧭 指令模式 (Prompting Patterns)

### 模式 A：文献调研 (Research)
> "请搜索关于 [主题] 的近三年核心期刊论文，并筛选出引用率最高的 5 篇，汇报其摘要。"
- **AI 执行逻辑**：调用 `cnki-standard` 检索 -> 调用 `cnki-verifier` 验证真实性 -> 整理报告。

### 模式 B：引文核实 (Fact-Check)
> "我写了一段话提到了以下论文：[论文标题]。请帮我核实它们在知网上是否存在，并补充其 DOI。"
- **AI 执行逻辑**：调用 `cnki-verifier` 逐一核对。

###模式 C：高级全自动流程 (Professional Workflow)
> "请在知网上打开《计算机学报》最新一期，列出所有标题，并将感兴趣的第 2 和第 5 篇下载并保存到我的 Zotero 中。"
- **AI 执行逻辑**：调用 `chrome-devtools` 模拟操作 -> 执行相关 Skill 脚本。

---

## ⚠️ 注意事项与合规性
1. **频率限制**：所有自动化操作应遵循低频原则，防止触发知网的反爬验证码。
2. **机构认证**：在执行下载操作前，确保您的浏览器已通过校园网/机构 VPN 登录。
3. **数据版权**：严禁利用此类工具进行大规模非法抓取或商业化分发。
