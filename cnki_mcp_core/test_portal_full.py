import asyncio
import os
import sys

# 注入当前目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.browser_pw import AsyncBrowserPool
from services.portal_service import login_shutong_portal
from services.search_service import execute_protocol_search

from dotenv import load_dotenv

# 加载 .env 凭据
load_dotenv()

async def run_portal_test():
    print("🚀 --- Skill_CNKI 书童门户 [显式交互模式] ---")
    print("📢 浏览器窗口已开启，请观察登录与跳转流程...")
    
    # 改为显式模式 (Headless=False) 以便观察
    os.environ["CNKI_HEADLESS"] = "false" 
    
    pool = AsyncBrowserPool(cookie_path="cookies_portal.json")
    
    try:
        page = await pool.get_page()
        
        # 1. 尝试门户登录 (从 .env 获取凭据)
        username = os.getenv("SHUTONG_CARD")
        password = os.getenv("SHUTONG_PASSWORD")
        
        if not username or not password:
            print("❌ 错误: 未在 .env 中找到 SHUTONG_CARD 或 SHUTONG_PASSWORD")
            return
        
        print("\n⏳ [1/2] 正在执行全自动登录 (OCR 识别模式)...")
        login_res, active_page = await login_shutong_portal(page, username, password)
        print(f"📊 登录阶段反馈: {login_res}")
        
        if "✅" not in login_res:
            print("❌ 授权流程中断。")
            return
            
        # 2. 验证知网权限 (必须在已授权的 Tab 上操作)
        print("\n🔍 [2/2] 正在验证授权后的检索能力...")
        keyword = "深度学习"
        results = await execute_protocol_search(active_page, keyword, "TI", "相关度")
        
        if results:
            print(f"✅ 验证成功！授权域名下成功检索到 {len(results)} 条结果。")
            print(f"   ∟ 第一条: {results[0]['title']}")
        else:
            print("⚠️ 检索结果为空，请检查 VPN 隧道是否稳定。")
            
        # 保存 Session
        await pool.save_cookies()
        print(f"✅ 门户 Session 已保存至: {pool.cookie_path}")

    except Exception as e:
        print(f"💥 测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        await pool.close()

if __name__ == "__main__":
    asyncio.run(run_portal_test())
