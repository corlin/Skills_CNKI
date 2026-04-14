from core.constants import SEARCH_MODES, SORT_MODES, SEARCH_PATH
from typing import List
from urllib.parse import urlparse, quote
from playwright.async_api import Page

def get_base_url(url: str) -> str:
    """从当前 URL 中提取协议、域名和端口"""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

async def parse_grid_row(row, base_url: str) -> dict:
    """异步解析海外版结果行数据"""
    try:
        title_elem = await row.query_selector("td.name a, .fz14 a")
        if not title_elem: return {}
        
        title = (await title_elem.text_content()).strip()
        url = await title_elem.get_attribute("href")
        if url and not url.startswith("http"):
            url = f"{base_url}{url}" if url.startswith("/") else f"{base_url}/{url}"
            
        # 作者
        author_elems = await row.query_selector_all("td.author a")
        authors = [(await a.text_content()).strip() for a in author_elems]
        
        # 来源与日期
        source_elem = await row.query_selector("td.source")
        source = (await source_elem.text_content()).strip() if source_elem else "未知"
        
        date_elem = await row.query_selector("td.date")
        date = (await date_elem.text_content()).strip() if date_elem else ""
        
        return {
            "title": title,
            "url": url,
            "authors": authors,
            "source": source,
            "date": date
        }
    except Exception as e:
        print(f"DEBUG: 解析行失败: {e}")
        return {}

async def execute_protocol_search(page: Page, query: str, mode: str, sort: str, retry_count: int = 2) -> List[dict]:
    base_url = get_base_url(page.url)
    for attempt in range(retry_count + 1):
        try:
            # 1. 构造 Direct URL (自适应 Base URL)
            direct_url = f"{base_url}{SEARCH_PATH}?kw={quote(query)}"
            print(f"🚀 [Playwright] 尝试 {attempt+1} 开启检索: {direct_url}")
            
            # 使用较宽松的加载等待条件以适配镜像站
            await page.goto(direct_url, wait_until="domcontentloaded", timeout=30000)
            
            # 2. 等待结果渲染
            try:
                await page.wait_for_selector("table.result-table-list, .fz14", timeout=15000)
            except:
                # 如果没搜到结果
                print("⚠️ 未发现结果容器，可能是无搜索结果。")
                return []
            
            # 3. 提取行
            rows = await page.query_selector_all("table.result-table-list tbody tr, .result-table-list-body tr")
            results = []
            for row in rows[:15]:
                info = await parse_grid_row(row, base_url)
                if info and info.get("title"):
                    results.append(info)
                    
            if not results:
                # 检查是否命中了 418 或者 验证码
                content = await page.content()
                if "418" in content or "机器人" in content:
                    raise Exception("检测到 418 拦截或机器人验证")
            
            return results
            
        except Exception as e:
            print(f"⚠️ Playwright 检索失败 (尝试 {attempt+1}): {e}")
            if attempt < retry_count:
                await asyncio.sleep(2)
            else:
                return []
