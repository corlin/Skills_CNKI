import os
import asyncio
import time
from playwright.async_api import Page, TimeoutError

async def execute_interactive_login(page: Page) -> str:
    """启动带界面的登录引导 (Playwright 版)"""
    # 引导至登录页
    login_url = "https://login.cnki.net/login/?platform=kns&RedirectURL=https://oversea.cnki.net/"
    print(f"🔑 [Playwright] 正在引导至登录页: {login_url}")
    
    await page.goto("https://oversea.cnki.net/", wait_until="networkidle")
    await page.goto(login_url, wait_until="networkidle")
    
    # 提示用户在可视化窗口操作
    print("📢 请在弹出的浏览器窗口中完成登录。系统将等待 60 秒...")
    await asyncio.sleep(60) 
    
    return "✅ 登录流程已结束，请检查是否成功已持久化。"

async def execute_download(page: Page, paper_url: str, download_dir: str) -> str:
    """使用 Playwright 处理文件下载"""
    try:
        await page.goto(paper_url, wait_until="networkidle")
        
        # 查找下载按钮 (海外版常见下载按钮文本或样式)
        # 优先寻找 PDF 下载按钮
        download_btn_selector = '//*[@id="pdfDown"]|//a[contains(text(),"PDF")]|//a[contains(@class,"download")]'
        
        btn = await page.wait_for_selector(download_btn_selector, timeout=10000)
        
        # 使用 Playwright 的 expect_download 捕捉下载事件
        async with page.expect_download() as download_info:
            await btn.click()
            
        download = await download_info.value
        file_path = os.path.join(download_dir, download.suggested_filename)
        await download.save_as(file_path)
        
        return f"🚀 下载成功: {file_path}"
    except Exception as e:
        return f"❌ 下载失败: {str(e)}"
