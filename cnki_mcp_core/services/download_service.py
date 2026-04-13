import os
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.browser import BrowserPool
from core.utils import get_safe_filename

def execute_interactive_login(pool: BrowserPool):
    """有界面浏览器交互登录"""
    # 强制关闭现有 headless 驱动，开启 headed 驱动
    pool.close()
    driver = pool.get_driver(headless=False)
    driver.get("https://login.cnki.net/login/?platform=kns&RedirectURL=https://www.cnki.net/")
    
    # 给用户 60 秒时间登录
    time.sleep(60) 
    pool.save_cookies()
    return "登录会话已保存。您现在可以关闭浏览器窗口或等待其自动回收。"

def execute_download(pool: BrowserPool, url: str) -> dict:
    """自动化下载流程"""
    driver = pool.get_driver()
    driver.get(url)
    
    # 1. 提取标题用于重命名
    try:
        title = driver.find_element(By.XPATH, '//div[@class="wx-tit"]/h1').text.strip()
        safe_title = get_safe_filename(title)
    except:
        safe_title = f"paper_{int(time.time())}"

    # 2. 寻找下载按钮 (优先 PDF)
    download_xpath = '//*[@id="pdfDown"] | //a[contains(@class, "pdf")] | //a[contains(text(), "PDF下载")]'
    
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, download_xpath))
        )
        
        # 安全延迟 (5-7秒)
        time.sleep(random.uniform(5, 7))
        
        btn.click()
        time.sleep(10) # 等待下载启动
        
        return {
            "status": "success",
            "filename": f"{safe_title}.pdf",
            "path": os.path.join(pool.download_dir, f"{safe_title}.pdf"),
            "message": "下载指令已发出，请检查 downloads 目录。"
        }
    except Exception as e:
        return {"status": "error", "message": f"未找到可用的下载链接或无权限: {str(e)}"}
