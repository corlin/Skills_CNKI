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
from services.portal_service import login_shutong_portal

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
async def export_to_zotero(
    url: str,
    ctx: Context,
    pool: AsyncBrowserPool = Depends(get_pool)
) -> str:
    """获取论文详情并导出为 RIS 格式 (Zotero 兼容)。"""
    await ctx.info(f"📤 正在导出元数据: {url}")
    page = await pool.get_page()
    try:
        detail = await fetch_paper_details(page, url)
        ris = _generate_ris(detail)
        return ris
    except Exception as e:
        return f"❌ 导出失败: {str(e)}"
    finally:
        await page.close()

@mcp.tool()
async def verify_paper(
    title: str,
    abstract: str,
    ctx: Context,
    pool: AsyncBrowserPool = Depends(get_pool)
) -> dict:
    """抗幻觉核验：根据标题和摘要检测论文的真实性。"""
    await ctx.info(f"🛡️ 正在核验文献真实性: {title}")
    page = await pool.get_page()
    try:
        # 直接利用搜索功能找标题
        results = await execute_protocol_search(page, title, "TI", "相关度")
        if not results:
            return {"status": "suspicious", "message": "未找到匹配论文，请警惕幻觉。", "similarity": 0}
        
        match = results[0]
        # 获取匹配论文的详情进行摘要对齐
        detail = await fetch_paper_details(page, match['url'])
        sim = calculate_similarity(abstract, detail.get('abstract', ''))
        
        status = "verified" if sim > 0.6 else "warning"
        return {
            "status": status,
            "similarity": round(sim, 2),
            "matched_title": match['title'],
            "matched_url": match['url'],
            "message": "文献真实存在。" if status == "verified" else "找到同名文献但摘要差异较大，请核实。"
        }
    except Exception as e:
        return {"status": "error", "message": f"核验异常: {str(e)}"}
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
        res = await execute_interactive_login(page)
        await pool.save_cookies()
        return f"{res}\n✅ Session 已持久化至 {pool.cookie_path}"
    finally:
        await page.close()

@mcp.tool()
async def login_via_portal(
    ctx: Context, 
    pool: AsyncBrowserPool = Depends(get_pool),
    username: str = "69023847", 
    password: str = "cylgame"
) -> str:
    """通过书童图书馆门户授权访问知网。内置 OCR 验证码识别。"""
    await ctx.info(f"🔑 正在启动书童门户授权流程 (账号: {username})...")
    
    page = await pool.get_page()
    try:
        res = await login_shutong_portal(page, username, password)
        await pool.save_cookies()
        return res
    except Exception as e:
        return f"❌ 门户登录异常: {str(e)}"
    finally:
        await page.close()

if __name__ == "__main__":
    mcp.run()
