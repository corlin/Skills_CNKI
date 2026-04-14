import asyncio
import os
import sys

# 注入当前目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.browser_pw import AsyncBrowserPool
from services.download_service import execute_interactive_login

async def test_interactive_login():
    print("🚀 --- Skill_CNKI 交互式登录回归测试 ---")
    print("📢 本测试将开启可视化浏览器窗口，请在其中完成登录。")
    
    # 强制关闭无头模式
    os.environ["CNKI_HEADLESS"] = "false"
    
    # 初始化环境
    pool = AsyncBrowserPool(cookie_path="cookies_pw.json")
    
    try:
        page = await pool.get_page()
        
        # 调用核心登录逻辑
        # 发现的有效海外登录地址 (解决 SSL 证书错误问题)
        login_url = "https://o.oversea.cnki.net/newOverseaLogin/overseasLogin.html?lang=en-US&platform=OVERSEAS_EN&ForceReLogin=1&ReturnURL=//oversea.cnki.net/"
        print(f"\n🔗 [1/3] 正在跳转至海外版知网登录页...")
        await page.goto("https://oversea.cnki.net/", wait_until="networkidle")
        await page.goto(login_url, wait_until="networkidle")
        
        print("\n🔑 [2/3] 请在弹出的窗口中进行登录 (可以使用手机扫码或账号登录)。")
        print("💡 登录成功跳转后，请在此时回到终端按下 Enter 键...")
        
        # 阻塞等待用户在终端输入
        await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        
        print("\n💾 [3/3] 正在保存 Session 信息...")
        await pool.save_cookies()
        
        # 验证一下是否真的登录成功了 (访问个人中心或首页检查标题)
        await page.goto("https://oversea.cnki.net/", wait_until="networkidle")
        title = await page.title()
        print(f"✅ 登录后首页验证: {title}")
        print(f"✅ Cookie 已保存至: {os.path.abspath(pool.cookie_path)}")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
    finally:
        print("\n🧹 正在释放资源并关闭窗口...")
        await pool.close()
        print("✨ 测试结束。")

if __name__ == "__main__":
    asyncio.run(test_interactive_login())
