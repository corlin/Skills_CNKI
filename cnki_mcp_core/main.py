import os
import asyncer
from typing import List
from dataclasses import dataclass
from contextlib import asynccontextmanager

from fastmcp import FastMCP, Context
from fastmcp.dependencies import Depends, CurrentContext

# 导入自定义模块
from core.browser import BrowserPool
from core.constants import SEARCH_MODES, SEARCH_MODE_ALIASES, SORT_MODES
from core.utils import calculate_similarity, _generate_ris

from services.search_service import execute_protocol_search
from services.detail_service import _get_paper_detail_sync
from services.download_service import execute_interactive_login, execute_download


# =================== MCP 核心管理 ===================

@dataclass
class AppContext:
    browser_pool: BrowserPool

@asynccontextmanager
async def lifespan(server: FastMCP):
    pool = BrowserPool()
    try:
        yield AppContext(browser_pool=pool)
    finally:
        pool.close()

mcp = FastMCP(
    "Skill_CNKI_Core",
    lifespan=lifespan,
    description="知网科研能力核心服务器 (模块化重构版)"
)

def get_pool(ctx: Context = CurrentContext()) -> BrowserPool:
    return ctx.request_context.lifespan_context.browser_pool


# =================== MCP 工具注册 ===================

@mcp.tool()
async def search_cnki(
    query: str, 
    ctx: Context,
    mode: str = "主题", 
    sort: str = "相关度",
    pool: BrowserPool = Depends(get_pool)
) -> dict:
    """
    搜索知网论文。支持主题、篇名、关键词、作者、DOI检索。
    """
    # 解析别名
    resolved_mode = SEARCH_MODE_ALIASES.get(mode.lower(), mode)
    if resolved_mode not in SEARCH_MODES:
        resolved_mode = "主题"
    
    await ctx.info(f"检索 '{query}' (模式: {resolved_mode}, 排序: {sort})...")
    results = await asyncer.asyncify(execute_protocol_search)(pool, query, resolved_mode, sort)
    
    return {"status": "success", "count": len(results), "results": results}

@mcp.tool()
async def get_paper_detail(url: str, ctx: Context, pool: BrowserPool = Depends(get_pool)) -> dict:
    """获取单篇论文的详细信息（摘要、关键词、DOI、被引频次等）。"""
    await ctx.info(f"解析详情: {url[:60]}...")
    return await asyncer.asyncify(_get_paper_detail_sync)(pool, url)

@mcp.tool()
async def verify_paper(title: str, ctx: Context, author: str = "", pool: BrowserPool = Depends(get_pool)) -> dict:
    """核验引文真实性（抗幻觉功能）。"""
    await ctx.info(f"核验引文: '{title[:50]}'")
    results = await asyncer.asyncify(execute_protocol_search)(pool, title, "主题", "相关度")
    
    if not results:
        return {"status": "warning", "confidence": "0%", "message": "未在知网找到任何匹配项。"}
    
    top_match = results[0]
    score = calculate_similarity(title, top_match['title'])
    
    confidence = "极低"
    if score > 0.9: confidence = "极高 (100% 匹配)"
    elif score > 0.7: confidence = "高"
    elif score > 0.4: confidence = "中"
    
    return {
        "status": "success",
        "match_score": f"{score*100:.1f}%",
        "confidence": confidence,
        "best_match": top_match
    }

@mcp.tool()
async def interactive_login(ctx: Context, pool: BrowserPool = Depends(get_pool)) -> str:
    """启动有界面浏览器进行手动或机构登录。"""
    return await asyncer.asyncify(execute_interactive_login)(pool)

@mcp.tool()
async def download_paper(url: str, ctx: Context, pool: BrowserPool = Depends(get_pool)) -> dict:
    """自动化下载指定 URL 的论文 PDF。"""
    await ctx.info(f"开始下载: {url[:50]}")
    return await asyncer.asyncify(execute_download)(pool, url)

@mcp.tool()
async def export_to_zotero(paper_data: dict, ctx: Context, pool: BrowserPool = Depends(get_pool)) -> dict:
    """导出 Zotero 兼容的 .ris 元数据文件。"""
    from core.utils import get_safe_filename
    title = paper_data.get("title", "unknown")
    filename = f"{get_safe_filename(title)}.ris"
    filepath = os.path.join(pool.download_dir, filename)
    
    ris_content = _generate_ris(paper_data)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(ris_content)
    
    return {"status": "success", "filename": filename, "path": filepath}

@mcp.tool()
async def check_status(ctx: Context, pool: BrowserPool = Depends(get_pool)) -> str:
    """检查知网核心连接状态。"""
    def _check():
        driver = pool.get_driver()
        driver.get("https://www.cnki.net/")
        return "浏览器实例就绪"
    status = await asyncer.asyncify(_check)()
    return f"✅ 核心框架运行正常！{status}"

if __name__ == "__main__":
    mcp.run()
