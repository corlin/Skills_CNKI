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
        """使用 undetected-chromedriver 创建破壁驱动"""
        import undetected_chromedriver as uc
        
        # 彻底隔离代理环境变量，防止封闭式 VPN 的强行注入
        for var in ["http_proxy", "https_proxy", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY"]:
            if var in os.environ:
                del os.environ[var]

        options = uc.ChromeOptions()
        if headless:
            options.add_argument("--headless") 
        
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--ignore-ssl-errors")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=zh-CN")

        # 强行绕过代理 (直连模式)
        if os.getenv("CNKI_DIRECT", "").lower() == "true":
            options.add_argument("--no-proxy-server")  # 完全不使用代理服务器
            options.add_argument("--proxy-server=direct://")
            options.add_argument("--proxy-bypass-list=*")

        # 随机化 User-Agent 以降低指纹关联
        selected_ua = random.choice(self._user_agents)
        options.add_argument(f'--user-agent={selected_ua}')
        
        # 禁用一些可能暴露自动化特征的参数
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-infobars")
        options.add_argument("--password-store=basic")
        options.add_argument("--no-first-run")
        
        # UC 自动下载对应的驱动并打补丁
        # 移除 version_main=146，启用自动环境适配以解决 M 芯片兼容性
        driver = uc.Chrome(options=options)
        driver.set_page_load_timeout(30)
        
        # 深度指纹混淆
        from selenium_stealth import stealth
        stealth(driver,
            languages=["zh-CN", "zh", "en"],
            vendor="Google Inc.",
            platform="MacIntel" if "Macintosh" in selected_ua else "Win32",
            webgl_vendor="Apple Inc." if "Macintosh" in selected_ua else "Intel Inc.",
            renderer="Apple M2" if "Macintosh" in selected_ua else "Intel Iris OpenGL Engine",
            fix_hairline=True,
            run_on_insecure_origins=True
        )
        return driver

    def get_driver(self, headless=None) -> webdriver.Chrome:
        """获取或创建驱动程序，包含自愈逻辑"""
        # 允许通过环境变量全局控制 headless 模式 (调试利器)
        env_headless = os.getenv("CNKI_HEADLESS", "").lower()
        if env_headless == "true":
            effective_headless = True
        elif env_headless == "false":
            effective_headless = False
        else:
            effective_headless = True if headless is None else headless

        with self._lock:
            now = time.time()
            
            # 健康检查：如果驱动已存但无响应或窗口丢失，强制关闭重开
            if self._driver:
                is_healthy = True
                try:
                    # 获取当前 URL 是最轻量级的健康探测
                    _ = self._driver.current_url 
                except Exception:
                    is_healthy = False
                
                if not is_healthy or (now - self._last_used > self.IDLE_TIMEOUT):
                    print("⚠️ 驱动失效或超时，正在执行自愈式重连...")
                    self.close()
            
            if not self._driver:
                self._driver = self._create_driver(headless=effective_headless)
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
                self._driver.get("https://oversea.cnki.net/")
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

    def clear_session(self):
        """物理清除本地 Cookie 文件，用于强制重置被标记的会话"""
        self.close()
        if os.path.exists(self.cookie_path):
            try:
                os.remove(self.cookie_path)
                print(f"🗑️ 已清理本地会话文件: {self.cookie_path}")
            except Exception as e:
                print(f"清理会话文件失败: {e}")
