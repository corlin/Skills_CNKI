import os
import time
import random
import threading
from typing import Optional
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class BrowserPool:
    """
    浏览器池 - 管理 Chrome 实例的复用与反爬策略
    """
    IDLE_TIMEOUT = 600  # 10 分钟无活动后自动关闭
    
    def __init__(self, cookie_path="cookies.json", download_dir="downloads"):
        self._driver: Optional[webdriver.Chrome] = None
        self._last_used: float = 0
        self._lock = threading.Lock()
        self.cookie_path = os.path.abspath(cookie_path)
        self.download_dir = os.path.abspath(download_dir)
        os.makedirs(self.download_dir, exist_ok=True)
        
        self._user_agents = [
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
        ]

    def _create_driver(self, headless=True) -> webdriver.Chrome:
        """创建注入反检测脚本的 Chrome 实例"""
        options = Options()
        if headless:
            options.add_argument("--headless=new") 
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"user-agent={random.choice(self._user_agents)}")
        
        # 下载配置
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "plugins.always_open_pdf_externally": True
        }
        options.add_experimental_option("prefs", prefs)
        
        # 隐藏自动化指纹
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # 移除 webdriver 特征
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                  get: () => undefined
                })
              """
        })
        return driver

    def get_driver(self, headless=True) -> webdriver.Chrome:
        """获取或创建驱动程序 (线程安全)"""
        with self._lock:
            now = time.time()
            if self._driver and (now - self._last_used > self.IDLE_TIMEOUT):
                self.close()
            
            if not self._driver:
                self._driver = self._create_driver(headless=headless)
                self.load_cookies()
            
            self._last_used = now
            return self._driver

    def save_cookies(self):
        """保存当前会话 Cookie 到本地数据文件"""
        if self._driver:
            import json
            try:
                cookies = self._driver.get_cookies()
                with open(self.cookie_path, 'w') as f:
                    json.dump(cookies, f)
            except Exception as e:
                print(f"保存 Cookie 失败: {e}")

    def load_cookies(self):
        """从本地数据文件加载会话 Cookie"""
        if self._driver and os.path.exists(self.cookie_path):
            import json
            try:
                self._driver.get("https://www.cnki.net/")
                with open(self.cookie_path, 'r') as f:
                    cookies = json.load(f)
                for cookie in cookies:
                    if 'expiry' in cookie: del cookie['expiry']
                    self._driver.add_cookie(cookie)
                self._driver.refresh()
            except Exception as e:
                print(f"加载 Cookie 失败: {e}")

    def close(self):
        """完全清理浏览器资源"""
        if self._driver:
            # self.save_cookies()
            try:
                self._driver.quit()
            except:
                pass
            self._driver = None
