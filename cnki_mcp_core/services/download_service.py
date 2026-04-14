import os
import asyncio
import time
from playwright.async_api import Page, TimeoutError

async def execute_interactive_login(page: Page) -> str:
    """启动带界面的登录引导 (Playwright 版)"""
    # 引导至海外版官网，让用户可以手动触发登录或直接访问有效登录页
    # 发现的有效海外登录地址：
    login_url = "https://o.oversea.cnki.net/newOverseaLogin/overseasLogin.html?lang=en-US&platform=OVERSEAS_EN&ForceReLogin=1&ReturnURL=//oversea.cnki.net/"
    
    print(f"🔑 [Playwright] 正在引导至海外版登录页...")
    
    # 先访问首页建立上下文
    await page.goto("https://oversea.cnki.net/", wait_until="networkidle")
    # 再跳转到正确的登录页
    await page.goto(login_url, wait_until="networkidle")
    
    # 提示用户在可视化窗口操作
    print("📢 请在弹出的浏览器窗口中完成登录。系统将等待 60 秒...")
    await asyncio.sleep(60) 
    
    return "✅ 登录流程已结束，请检查是否成功已持久化。"

async def execute_download(page: Page, paper_url: str, download_dir: str) -> str:
    """
    使用 Playwright 处理文件下载。
    支持：下拉菜单展开、多标签页监听、结算页识别、权限/余额不足智能诊断。
    """
    try:
        await page.goto(paper_url, wait_until="networkidle")
        
        # 1. 探测并定位下载菜单/按钮
        # 海外版可能直显 PDF 按钮，也可能隐藏在 Download 下拉菜单中
        main_download_btn_selector = '#pdfDown, .download, a:has-text("Download")'
        pdf_item_selector = 'a:has-text("PDF"), #pdfDown'
        
        try:
            # 尝试点击主按钮以展开菜单（主要针对有下拉交互的布局）
            await page.click(main_download_btn_selector, timeout=5000)
            await asyncio.sleep(1) # 等待动画
        except:
            pass # 如果没有下拉逻辑，直接寻找 PDF 链接即可

        # 2. 监听新打开的下载/计费标签页
        try:
            async with page.expect_popup(timeout=10000) as popup_info:
                # 寻找并点击真正的 PDF 链接
                pdf_btn = await page.wait_for_selector(pdf_item_selector, timeout=5000)
                await pdf_btn.click()
            
            new_page = await popup_info.value
            await new_page.wait_for_load_state("networkidle")
            
            # 3. 深度诊断新页面行为
            current_url = new_page.url
            page_content = await new_page.content()
            
            # 检查是否为结算/计费页 (典型路径: barnew/fee_O_GB.html)
            if "fee_O_GB" in current_url or "fee" in current_url.lower():
                # 检测余额不足提示
                if "insufficient" in page_content.lower() or "Balance is 0" in page_content:
                    return "❌ 下载失败: 账户余额不足。该文献需要支付积分，请充值或使用校外访问/机构包库账号。"
                return f"⚠️ 下载拦截: 已跳转至结算页 ({current_url})，请确认账户是否有下载权限。"

            # 如果新页面直接触发了下载
            try:
                # 在新页面上下文中捕获下载事件
                async with new_page.expect_download(timeout=15000) as download_info:
                    # 有些页面需要二次点击“立即下载”
                    now_download_btn = await new_page.query_selector('a:has-text("Download Now"), #downloadBtn')
                    if now_download_btn:
                        await now_download_btn.click()
                
                download = await download_info.value
                file_path = os.path.join(download_dir, download.suggested_filename)
                await download.save_as(file_path)
                return f"🚀 下载成功: {file_path}"
            except Exception:
                return f"❌ 下载失败: 已打开下载页但未探测到文件流。当前页面: {new_page.url}"

        except TimeoutError:
             return "❌ 下载失败: 点击下载后未响应。请检查账号是否已登录或知网是否弹出验证码。"
            
    except Exception as e:
        return f"❌ 下载过程中发生异常: {str(e)}"
