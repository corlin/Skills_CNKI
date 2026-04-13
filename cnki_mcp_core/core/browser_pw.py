import os
import json
import asyncio
import inspect
import playwright_stealth
from typing import Optional
from playwright.async_api import async_playwright, Browser, BrowserContext, Page

class AsyncBrowserPool:
    """
    Playwright 异步浏览器池 - 终极稳定版
    """
    def __init__(self, cookie_path="cookies_pw.json", download_dir="downloads"):
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        
        self.cookie_path = os.path.abspath(cookie_path)
        self.download_dir = os.path.abspath(download_dir)
        os.makedirs(self.download_dir, exist_ok=True)
        
        self._user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36"

    async def _ensure_browser(self, headless: bool = True):
        """确保浏览器和上下文已初始化"""
        if not self._playwright:
            self._playwright = await async_playwright().start()
            
        if not self._browser:
            self._browser = await self._playwright.chromium.launch(
                headless=headless,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-blink-features=AutomationControlled",
                    "--ignore-certificate-errors"
                ]
            )
            
        if not self._context:
            storage_state = None
            if os.path.exists(self.cookie_path):
                storage_state = self.cookie_path
            
            self._context = await self._browser.new_context(
                user_agent=self._user_agent,
                viewport={'width': 1920, 'height': 1080},
                storage_state=storage_state,
                accept_downloads=True
            )

    async def get_page(self) -> Page:
        """获取并配置隐身能力的 Page"""
        headless = os.getenv("CNKI_HEADLESS", "true").lower() == "true"
        await self._ensure_browser(headless=headless)
        
        page = await self._context.new_page()
        
        # --- 万能 Stealth 加载逻辑 (深度解析模块成员) ---
        try:
            target_func = None
            # 探测顶级成员
            for name in ['stealth_async', 'stealth', 'async_api']:
                attr = getattr(playwright_stealth, name, None)
                if not attr: continue
                if callable(attr) and not inspect.ismodule(attr):
                    target_func = attr; break
                if inspect.ismodule(attr):
                    # 尝试探测模块内部署的同名函数
                    sub_attr = getattr(attr, name, None)
                    if callable(sub_attr):
                        target_func = sub_attr; break
            
            if target_func:
                res = target_func(page)
                if inspect.isawaitable(res): await res
            else:
                from playwright_stealth import Stealth
                await Stealth().stealth(page)
        except Exception as e:
            pass # 即使失败也不再打印烦人的告警
            
        # 注入基础反爬脚本
        await page.add_init_script("delete Object.getPrototypeOf(navigator).webdriver")
        return page

    async def save_cookies(self):
        if self._context:
            await self._context.storage_state(path=self.cookie_path)

    async def close(self):
        if self._context: await self._context.close()
        if self._browser: await self._browser.close()
        if self._playwright: await self._playwright.stop()
        self._context = self._browser = self._playwright = None

    async def clear_session(self):
        await self.close()
        if os.path.exists(self.cookie_path):
            os.remove(self.cookie_path)
