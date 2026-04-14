import asyncio
import os
import sys

# 将当前目录添加到路径中以便导入
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.browser_pw import AsyncBrowserPool
from core.utils import _generate_ris
from services.search_service import execute_protocol_search
from services.detail_service import fetch_paper_details
from services.download_service import execute_download

async def run_comprehensive_test():
    print("🚀 --- Skill_CNKI 综合功能自动化测试 ---")
    
    # 设置环境变量为无头模式
    os.environ["CNKI_HEADLESS"] = "true"
    
    pool = AsyncBrowserPool()
    
    try:
        # 1. 连通性测试
        print("\n📡 [1/5] 检查首页连通性...")
        page = await pool.get_page()
        await page.goto("https://oversea.cnki.net/", wait_until="networkidle", timeout=20000)
        title = await page.title()
        print(f"✅ 首页访问成功: {title}")
        
        # 2. 搜索测试
        keyword = "深层学习"
        print(f"\n🔍 [2/5] 正在搜索关键词: '{keyword}'...")
        results = await execute_protocol_search(page, keyword, "TI", "相关度")
        
        if not results:
            print("❌ 搜索失败: 未获取到结果。")
            return
            
        print(f"✅ 搜索成功！获取到 {len(results)} 条结果。")
        first_paper = results[0]
        print(f"   ∟ 第一条题目: {first_paper['title']}")
        
        # 3. 详情解析测试
        print(f"\n📄 [3/5] 正在解析文献详情: {first_paper['title']}...")
        detail = await fetch_paper_details(page, first_paper['url'])
        
        if detail.get('abstract'):
            print("✅ 详情解析成功！")
            # 合并结果供后续 RIS 使用
            paper_data = {**first_paper, **detail}
        else:
            print("⚠️ 详情解析部分成功，未获取到完整摘要。")
            paper_data = {**first_paper, **detail}

        # 4. RIS 导出测试
        print("\n📥 [4/5] 验证 RIS 导出逻辑...")
        ris_content = _generate_ris(paper_data)
        if "TY  - JOUR" in ris_content and paper_data['title'] in ris_content:
            print("✅ RIS 生成成功！预览:")
            print("-" * 30)
            print("\n".join(ris_content.split("\n")[:5]) + "\n...")
            print("-" * 30)
        else:
            print("❌ RIS 生成失败。")

        # 5. 下载逻辑验证
        print("\n⏳ [5/5] 验证下载流程逻辑 (寻找下载按钮)...")
        # 直接使用详情页尝试下载
        download_result = await execute_download(page, first_paper['url'], pool.download_dir)
        print(f"📡 下载结果反馈: {download_result}")

        print("\n✨ --- 综合测试运行结束 ---")

    except Exception as e:
        print(f"\n💥 测试异常退出: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        print("\n🧹 释放浏览器实例...")
        await pool.close()

if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())
