import time
from typing import List
from urllib.parse import quote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.constants import SEARCH_MODES, SORT_MODES
from core.browser import BrowserPool

def parse_grid_row(row) -> dict:
    """解析知网结果表格行数据"""
    try:
        title_elem = row.find_element(By.CSS_SELECTOR, "td.name a")
        title = title_elem.text.strip()
        url = title_elem.get_attribute("href")
        
        authors = [a.text.strip() for a in row.find_elements(By.CSS_SELECTOR, "td.author a")]
        source = row.find_element(By.CSS_SELECTOR, "td.source").text.strip()
        date = row.find_element(By.CSS_SELECTOR, "td.date").text.strip()
        
        return {
            "title": title,
            "url": url,
            "authors": authors,
            "source": source,
            "date": date
        }
    except:
        return {}

def execute_protocol_search(pool: BrowserPool, query: str, mode: str, sort: str) -> List[dict]:
    """执行协议级搜索流程"""
    driver = pool.get_driver()
    
    # 构建 Starter URL
    field = SEARCH_MODES.get(mode, "SU")
    starter_url = f"https://kns.cnki.net/starter?rc=CJFQ&kw={quote(query)}&rt=journal&fd={field}"
    
    driver.get(starter_url)
    
    # 等待结果表格加载 (Grid 模式)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table.result-table-list"))
        )
        
        # 应用排序 (如果非默认)
        if sort in SORT_MODES and sort != "相关度":
            sort_id = SORT_MODES[sort]
            driver.find_element(By.ID, sort_id).click()
            time.sleep(2) # 等待重新加载
            
        rows = driver.find_elements(By.CSS_SELECTOR, "table.result-table-list tbody tr")
        results = []
        for row in rows[:15]: # 限制一页结果
            info = parse_grid_row(row)
            if info:
                results.append(info)
        return results
    except Exception as e:
        print(f"搜索发生错误: {e}")
        return []
