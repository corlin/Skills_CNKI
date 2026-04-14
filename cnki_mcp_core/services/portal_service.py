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
    portal_url = "http://3.shutong2.com/"
    
    print(f"📥 [Portal] 正在启动书童图书馆入口: {portal_url}")
    
    for attempt in range(1, max_retries + 1):
        try:
            await page.goto(portal_url, wait_until="networkidle", timeout=20000)
            
            # --- 1. 填充表单 ---
            await page.fill("input#user_name", username)
            await page.fill("input#password", password)
            
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
            await asyncio.gather(
                page.wait_for_load_state("networkidle"),
                page.click("input#ok")
            )
            
            # --- 4. 检查登录结果 ---
            content = await page.content()
            if "登录成功" in content or "个人中心" in content or "会员中心" in content:
                print("✅ [Portal] 登录成功！")
                break
            elif "验证码错误" in content:
                print("❌ [Portal] 验证码识别错误，正在重试...")
                continue
            else:
                # 检查是否已经跳转到首页
                if "/index.php" in page.url or "user" not in page.url:
                    break
        except Exception as e:
            print(f"⚠️ [Portal] 登录尝试异常: {str(e)}")
            if attempt == max_retries: raise e

    # --- 5. 导航至知网入口 ---
    print("🚀 [Portal] 正在通过 '知网入口3（推荐）' 建立授权隧道...")
    try:
        # 进入中文库
        await page.goto("http://3.shutong2.com/zhongwenku/", wait_until="domcontentloaded")
        
        # 点击推荐入口 3
        # 针对镜像站，我们降低等待条件为 'domcontentloaded'，并在超时发生时进行补救探测
        try:
            async with page.expect_navigation(wait_until="domcontentloaded", timeout=25000):
                await page.click('a[href="/api33.php"]')
        except TimeoutError:
            print("⚠️ [Portal] 跳转超时，正在尝试主动识别知网特征...")

        # 验证是否进入了知网（无论是海外版还是镜像站，标题或搜索框应存在）
        # 等待搜索框出现
        try:
            await page.wait_for_selector('input#txt_SearchText, input[name="kw"]', timeout=10000)
            is_success = True
        except:
            is_success = "cnki" in page.url.lower()

        if is_success:
            final_url = page.url
            final_title = await page.title()
            print(f"🎯 [Portal] 授权链路就绪！")
            print(f"   ∟ 镜像域名: {final_url}")
            print(f"   ∟ 页面标题: {final_title}")
            return f"✅ 授权成功！当前镜像站: {final_url}"
        else:
            return f"❌ 无法识别知网特征，当前 URL: {page.url}"
        
    except Exception as e:
        return f"❌ 门户授权跳转失败: {str(e)}"
