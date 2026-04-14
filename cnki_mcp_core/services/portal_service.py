import asyncio
import os
import time
from playwright.async_api import Page, TimeoutError
from core.ocr_helper import OCRHelper

async def login_shutong_portal(page: Page, username, password, max_retries=3) -> str:
    """
    书童图书馆全自动登录集成 (包含 OCR 验证码处理)
    """
    ocr = OCRHelper()
    portal_url = "https://3.shutong2.com/"
    
    print(f"📥 [Portal] 正在启动书童图书馆入口: {portal_url}")
    
    for attempt in range(1, max_retries + 1):
        try:
            # 优先使用 https 协议以获得更快的响应
            await page.goto(portal_url, wait_until="domcontentloaded", timeout=25000)
            
            # --- 1. 填充表单 (增加内容清理，防止残留导致卡号堆叠) ---
            user_input = await page.wait_for_selector("input#user_name", timeout=10000)
            await user_input.click(click_count=3)
            await user_input.press("Backspace")
            await user_input.fill(username)
            
            pwd_input = await page.wait_for_selector("input#password", timeout=5000)
            await pwd_input.click(click_count=3)
            await pwd_input.press("Backspace")
            await pwd_input.fill(password)
            
            # --- 2. 识别验证码 ---
            captcha_img = await page.wait_for_selector('img[src*="/e/ShowKey/"]', timeout=5000)
            img_bytes = await captcha_img.screenshot()
            
            captcha_text = ocr.classify_image_element(img_bytes)
            print(f"🧩 [OCR] 识别验证码 (尝试 {attempt}/{max_retries}): {captcha_text}")
            
            if not captcha_text:
                print("⚠️ [OCR] 识别结果为空，正在刷新...")
                await captcha_img.click()
                continue
                
            await page.fill("input#code", captcha_text)
            
            # --- 3. 提交登录 ---
            # 点击登录，不强制等待 networkidle，因为后续会有重定向
            await page.click("input#ok")
            
            # --- 4. 检查登录结果 ---
            # 登录后的重定向可能比较慢，探测关键标志
            try:
                # 等待进入主页或提示登录成功
                await page.wait_for_selector('text="登录成功", text="个人中心", text="退出", .top-user', timeout=10000)
                print("✅ [Portal] 登录成功！")
                break
            except:
                content = await page.content()
                if "验证码错误" in content:
                    print("❌ [Portal] 验证码识别错误，正在重试...")
                    continue
        except Exception as e:
            print(f"⚠️ [Portal] 登录尝试异常: {str(e)}")
            if attempt == max_retries: raise e

    # --- 5. 导航至知网入口 ---
    print("🚀 [Portal] 正在进入资源目录并建立授权隧道...")
    try:
        # 直接使用 https 入口
        if "zhongwenku" not in page.url:
            await page.goto("https://3.shutong2.com/zhongwenku/", wait_until="domcontentloaded", timeout=30000)
        
        # 显式等待入口 3 链接出现
        print("⏳ [Portal] 正在定位知网授权入口...")
        entry_selector = 'a[href="/api33.php"]'
        await page.wait_for_selector(entry_selector, state="visible", timeout=15000)
        
        # 点击推荐入口 3
        # 针对镜像站可能使用 target="_blank" 打开新标签页的情况，增加弹出窗口监听
        print("🚀 [Portal] 点击知网入口 3，正在监听弹出窗口/页面跳转 (最高等待 60s)...")
        
        target_page = page
        try:
            # 同时监听当前页面跳转和新页面弹出
            async with page.context.expect_page(timeout=60000) as new_page_info:
                await page.click(entry_selector)
            target_page = await new_page_info.value
            print(f"✨ [Portal] 检测到新授权窗口弹出: {target_page.url}")
        except TimeoutError:
            print("⚠️ [Portal] 未检测到新窗口弹出，继续在当前页面尝试识别...")
        except Exception as e:
            print(f"⚠️ [Portal] 弹出窗口获取异常: {str(e)}")

        # 验证是否进入了知网镜像 (在目标窗口执行探测)
        try:
            # 探测知网通用搜索框
            await target_page.wait_for_selector('input#txt_SearchText, input[name="kw"], #btnSearch', timeout=20000)
            is_success = True
        except:
            # 备选：根据域名判定 (包含 wvpn 或 cnki)
            current_url = target_page.url.lower()
            is_success = "cnki" in current_url or "wvpn" in current_url

        if is_success:
            final_url = target_page.url
            final_title = await target_page.title()
            print(f"🎯 [Portal] 授权链路就绪！当前地址: {final_url}")
            
            # 如果是弹出窗口，确保后续操作可以继承状态
            if target_page != page:
                await target_page.bring_to_front()
                
            return f"✅ 授权成功！当前镜像站: {final_url}", target_page
        else:
            return f"❌ 授权失败：无法在页面识别知网特征。URL: {target_page.url}", page
        
    except Exception as e:
        return f"❌ 门户授权流程中断: {str(e)}", page
