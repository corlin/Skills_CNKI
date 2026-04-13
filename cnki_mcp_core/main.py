import os
import asyncio
from typing import List
from dataclasses import dataclass
from contextlib import asynccontextmanager

from fastmcp import FastMCP, Context
from fastmcp.dependencies import Depends, CurrentContext

# 导入新的异步核心
from core.browser_pw import AsyncBrowserPool
from core.constants import SEARCH_MODES, SEARCH_MODE_ALIASES, SORT_MODES
from core.utils import calculate_similarity, _generate_ris

from services.search_service import execute_protocol_search
from services.detail_service import fetch_paper_details
from services.download_service import execute_interactive_login, execute_download

@dataclass
class AppContext:
    browser_pool: AsyncBrowserPool

@asynccontextmanager
async def lifespan(server: FastMCP):
    pool = AsyncBrowserPool()
    try:
        yield AppContext(browser_pool=pool)
    finally:
        await pool.close()

mcp = FastMCP(
    "Skill_CNKI_Core",
    lifespan=lifespan
)

def get_pool(ctx: Context = CurrentContext()) -> AsyncBrowserPool:
    return ctx.request_context.lifespan_context.browser_pool

# =================== MCP 工具注册 ===================

@mcp.tool()
async def search_cnki(
    query: str, 
    ctx: Context,
    mode: str = "主题", 
    sort: str = "相关度",
    pool: AsyncBrowserPool = Depends(get_pool)
) -> dict:
    """搜索知网论文 (Playwright 异步驱动)。支持中英文检索模式。"""
    resolved_mode = SEARCH_MODE_ALIASES.get(mode.lower(), mode)
    if resolved_mode not in SEARCH_MODES:
        resolved_mode = "主题"
    
    await ctx.info(f"🔎 正在海外版检索 '{query}'...")
    
    page = await pool.get_page()
    try:
        results = await execute_protocol_search(page, query, resolved_mode, sort)
        return {"status": "success", "count": len(results), "results": results}
    except Exception as e:
        return {"status": "error", "message": f"详情获取异常: {str(e)}"}
    finally:
        await page.close()

@mcp.tool()
async def get_paper_details(
    url: str, 
    ctx: Context,
    pool: AsyncBrowserPool = Depends(get_pool)
) -> dict:
    """获取指定论文的详情（摘要、关键词、DOI 等）。"""
    await ctx.info(f"📄 正在解析详情: {url}")
    
    page = await pool.get_page()
    try:
        detail = await fetch_paper_details(page, url)
        return {"status": "success", "data": detail}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        await page.close()

@mcp.tool()
async def download_paper(
    url: str, 
    ctx: Context,
    pool: AsyncBrowserPool = Depends(get_pool)
) -> str:
    """下载指定 URL 的论文 PDF。"""
    await ctx.info(f"⏳ 正在启动下载任务: {url}...")
    
    page = await pool.get_page()
    try:
        result = await execute_download(page, url, pool.download_dir)
        return result
    except Exception as e:
        return f"❌ 下载过程中发生异常: {str(e)}"
    finally:
        await page.close()

@mcp.tool()
async def check_status(ctx: Context, pool: AsyncBrowserPool = Depends(get_pool)) -> str:
    """检查知网核心连接状态 (Playwright 版)。"""
    try:
        page = await pool.get_page()
        await page.goto("https://oversea.cnki.net/", wait_until="networkidle", timeout=15000)
        title = await page.title()
        await page.close()
        return f"✅ Playwright 驱动运行正常！首页标题: {title}"
    except Exception as e:
        return f"❌ 驱动异常或连接超时: {str(e)}"

@mcp.tool()
async def interactive_login(ctx: Context, pool: AsyncBrowserPool = Depends(get_pool)) -> str:
    """启动调试界面进行登录（如果需要）。"""
    # 这里建议用户设置环境变量
    if os.getenv("CNKI_HEADLESS", "true").lower() == "true":
        return "⚠️ 请设置环境变量 CNKI_HEADLESS=false 并重启服务以开启可视化登录界面。"
    
    page = await pool.get_page()
    try:
        return await execute_interactive_login(page)
    finally:
        await page.close()

if __name__ == "__main__":
    mcp.run()
