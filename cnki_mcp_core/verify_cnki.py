import asyncio
import os
from core.browser_pw import AsyncBrowserPool
from services.search_service import execute_protocol_search
from services.detail_service import fetch_paper_details

async def verify():
    print("🚀 --- CNKI MCP 全链路功能验证 ---")
    
    # 强制设置无头模式，避免干扰验证
    os.environ["CNKI_HEADLESS"] = "true"
    
    pool = AsyncBrowserPool()
    print("📡 [1/3] 正在启动 Playwright 异步物理引擎...")
    page = await pool.get_page()
    
    try:
        # 1. 验证搜索
        keyword = "大语言模型"
        print(f"🔍 [2/3] 正在验证海外版检索, 关键词: '{keyword}'...")
        results = await execute_protocol_search(page, keyword, "TI", "相关度")
        
        if not results:
            print("❌ 搜索失败: 未能获取到结果列表。")
            return

        print(f"✅ 搜索成功！获取到 {len(results)} 条结果。")
        first_paper = results[0]
        print(f"   ∟ 第一条题目: {first_paper['title']}")
        print(f"   ∟ 链接: {first_paper['url']}")

        # 2. 验证详情解析
        print(f"\n📄 [3/3] 正在验证详情页解析, 目标: {first_paper['title']}...")
        detail = await fetch_paper_details(page, first_paper['url'])
        
        if detail.get('abstract'):
            print("✅ 详情解析成功！")
            print(f"   ∟ 摘要 (前50字): {detail['abstract'][:50]}...")
            print(f"   ∟ 关键词: {', '.join(detail.get('keywords', []))}")
            if detail.get('doi'):
                print(f"   ∟ DOI: {detail['doi']}")
        else:
            print("⚠️ 详情解析部分成功，但未能提取到摘要。")

        print("\n✨ --- 验证全部完成，系统状态: 完美 [Green] ---")

    except Exception as e:
        print(f"\n❌ 验证过程中发生异常: {str(e)}")
    finally:
        print("\n🧹 正在释放资源...")
        await pool.close()

if __name__ == "__main__":
    asyncio.run(verify())
