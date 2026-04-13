import asyncio
from typing import Optional
from playwright.async_api import Page, TimeoutError

async def fetch_paper_details(page: Page, url: str) -> dict:
    """使用 Playwright 异步获取论文详情 (元数据解析)"""
    try:
        print(f"📄 [Playwright] 正在访问详情页: {url}")
        # 跳转并等待关键元素
        await page.goto(url, wait_until="networkidle", timeout=20000)
        
        # 定义选择器映射
        selectors = {
            "abstract": '//*[@id="ChDivSummary"]|//div[@class="abstract-text"]',
            "keywords": '//div[@class="keywords"]//a|//span[@class="abstract-row"]//a',
            "doi": '//div[contains(@class,"top-tip")]//li[contains(text(),"DOI")]/span|//span[@id="resbd_doi"]'
        }
        
        # 提取摘要
        abstract = ""
        try:
            abs_elem = await page.wait_for_selector(selectors["abstract"], timeout=5000)
            if abs_elem:
                abstract = (await abs_elem.text_content()).strip()
        except: pass
            
        # 提取关键词
        kw_elems = await page.query_selector_all(selectors["keywords"])
        keywords = [(await kw.text_content()).strip() for kw in kw_elems]
        
        # 提取 DOI (如果有)
        doi = ""
        try:
            doi_elem = await page.query_selector(selectors["doi"])
            if doi_elem:
                doi = (await doi_elem.text_content()).strip()
        except: pass

        return {
            "abstract": abstract,
            "keywords": keywords,
            "doi": doi
        }
    except Exception as e:
        print(f"⚠️ [Playwright] 解析详情失败: {e}")
        return {}
