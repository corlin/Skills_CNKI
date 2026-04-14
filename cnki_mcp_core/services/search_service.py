import asyncio
from typing import List
from urllib.parse import urlparse
from playwright.async_api import Page, TimeoutError
from core.constants import SEARCH_MODES, SORT_MODES, SEARCH_PATH, HOME_PATH

def get_base_url(url: str) -> str:
    """提取当前页面的基础 URL"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

async def parse_grid_row(row, base_url: str) -> dict:
    """自适应解析文献行数据 (KNS8s 简体版 & Oversea 海外版)"""
    try:
        # 1. 标题 (KNS8s: a.fz14)
        title_elem = await row.query_selector("a.fz14, td.name a")
        if not title_elem: return {}
        
        title = (await title_elem.text_content()).strip()
        url = await title_elem.get_attribute("href")
        if url and not url.startswith("http"):
            url = f"{base_url}{url}" if url.startswith("/") else f"{base_url}/{url}"
            
        # 2. 作者 (KNS8s: a.KnowledgeNetLink)
        author_elems = await row.query_selector_all("td.author a, a.KnowledgeNetLink")
        authors = [(await a.text_content()).strip() for a in author_elems if (await a.text_content()).strip()]
        
        # 3. 来源 (期刊/会议)
        source_elem = await row.query_selector("td.source, td.journal a, .paper-source a")
        source = (await source_elem.text_content()).strip() if source_elem else "未知"
        
        # 4. 日期
        date_elem = await row.query_selector("td.date, .date-column")
        date = (await date_elem.text_content()).strip() if date_elem else ""
        
        return {
            "title": title,
            "url": url,
            "authors": authors,
            "source": source,
            "date": date
        }
    except Exception as e:
        print(f"DEBUG: 解析行解析失败: {e}")
        return {}

async def execute_protocol_search(page: Page, query: str, mode: str, sort: str, retry_count: int = 1) -> List[dict]:
    """
    交互式模拟检索 (核心重构):
    由于镜像站屏蔽了 URL 参数传参，必须通过 UI 物理输入点击来维持 Session。
    """
    base_url = get_base_url(page.url)
    
    for attempt in range(retry_count + 1):
        try:
            # 1. 回到知网主页 (确保 Session 处于主站上下文)
            # 有些镜像站主页可能就是结果页框架，灵活判断
            if "index" not in page.url.lower() and "DefaultResult" not in page.url:
                 await page.goto(f"{base_url}{HOME_PATH}", wait_until="domcontentloaded", timeout=20000)

            print(f"🔍 [Search] 正在执行交互式搜索 (尝试 {attempt+1}): '{query}'")
            
            # 2. 模拟输入 (适配 KNS8s 简体版主页与结果页的 ID 差异)
            # 主页通常是 input#txt_SearchText, 结果页顶部通常是 input#txt_search
            search_input = await page.wait_for_selector('input#txt_search, input#txt_SearchText, input[name="kw"], .search-input', timeout=10000)
            
            # 点击并清理
            await search_input.click(click_count=3)
            await search_input.press("Backspace")
            
            # 填入关键词并模拟按键
            await search_input.fill(query)
            await asyncio.sleep(0.5) 
            
            # 3. 点击搜索按钮 (KNS8s 标准类名)
            search_btn = await page.query_selector('input.search-btn, .search-btn, #btnSearch')
            if search_btn:
                await search_btn.click()
            else:
                await search_input.press("Enter")
            
            # 4. 耐心等待结果渲染 (镜像站通过 AJAX 注入)
            print("⏳ [Search] 等待 AJAX 数据注入...")
            try:
                # 等待列表容器渲染
                await page.wait_for_selector("table.result-table-list, table.grid-table-list", timeout=20000)
                # 等待数据行出现
                await page.wait_for_selector("a.fz14, td.name a", timeout=15000)
            except TimeoutError:
                # 检查是否是真的没有结果
                content = await page.content()
                if "未提取到" in content or "没有找到" in content:
                    print("⚠️ 确认无检索结果。")
                    return []
                raise Exception("数据行加载超时")

            # 5. 提取并解析结果
            rows = await page.query_selector_all("tr[grid-manager-td-index], table.result-table-list tbody tr, .result-table-list-body tr")
            results = []
            for row in rows[:15]:
                info = await parse_grid_row(row, base_url)
                if info and info.get("title"):
                    results.append(info)
                    
            if results:
                print(f"✅ 检索成功: 获取到 {len(results)} 条结果。")
                return results
            
        except Exception as e:
            print(f"⚠️ 交互式检索异常 (尝试 {attempt+1}): {str(e)}")
            if attempt < retry_count:
                # 强制刷新重试
                await page.reload(wait_until="domcontentloaded")
                await asyncio.sleep(2)
            else:
                return []
    return []
