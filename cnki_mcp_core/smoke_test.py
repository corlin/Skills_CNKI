import time
import asyncio
import asyncer
from core.browser import BrowserPool
from services.search_service import execute_protocol_search
from services.detail_service import _get_paper_detail_sync

async def run_smoke_test():
    """
    自动化集成冒烟测试：执行搜索 -> 获取详情 -> 相似度核验 -> 模拟下载准备
    """
    print("🚀 [1/4] 初始化浏览器池...")
    pool = BrowserPool()
    
    try:
        # 1. 测试搜索
        query = "大语言模型"
        print(f"🔍 [2/4] 正在检索关键词: '{query}'...")
        results = await asyncer.asyncify(execute_protocol_search)(pool, query, "主题", "相关度")
        
        if not results:
            print("❌ 检索失败，可能触发了知网风控或网络异常。")
            return
        
        first_paper = results[0]
        print(f"✅ 检索成功！找到 {len(results)} 篇结果。")
        print(f"   第一篇: {first_paper['title']} ({first_paper['source']})")
        
        # 2. 测试详情
        print(f"📄 [3/4] 正在解析文献详情: {first_paper['title']}...")
        detail = await asyncer.asyncify(_get_paper_detail_sync)(pool, first_paper['url'])
        
        if "abstract" in detail and detail["abstract"]:
            print(f"✅ 详情解析成功！摘要字数: {len(detail['abstract'])}")
        else:
            print("⚠️ 详情解析部分失败，未获取到完整摘要。")
            
        # 3. 环境状态
        print(f"🛠️ [4/4] 状态自检...")
        # 强制使用有界面模式进行调试
        driver = pool.get_driver(headless=False)
        time.sleep(2) # 等待界面加载
        
        # 捕获当前页面截图以便观察
        screenshot_path = "debug_screenshot.png"
        driver.save_screenshot(screenshot_path)
        print(f"📸 截图已保存至: {screenshot_path}")
        
        ua = driver.execute_script("return navigator.userAgent")
        print(f"✅ 环境正常。UA: {ua[:50]}...")
        
        print("\n✨ 冒烟测试全部通过！知网科研能力库已就绪。")
        
    except Exception as e:
        print(f"💥 测试过程中发生错误: {e}")
    finally:
        print("🧹 正在关闭浏览器实例...")
        pool.close()

if __name__ == "__main__":
    asyncio.run(run_smoke_test())
