from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from core.browser import BrowserPool

def _get_paper_detail_sync(pool: BrowserPool, url: str) -> dict:
    """获取论文详情页的深入元数据"""
    driver = pool.get_driver()
    driver.get(url)
    
    paper = {"url": url}
    try:
        # 等待关键内容加载 (摘要区域)
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="ChDivSummary"]|//div[@class="abstract-text"]'))
        )
        
        # 基础元数据解析
        selectors = {
            "title": '//div[@class="wx-tit"]/h1',
            "authors": '//h3[@class="author"]/span/a',
            "abstract": '//*[@id="ChDivSummary"]',
            "keywords": '//p[@class="keywords"]/a',
            "source": '//div[@class="top-tip"]//a[contains(@href, "navi.cnki.net")]',
            "doi": '//li[contains(@class, "top-space") and contains(., "DOI")]/p'
        }
        
        for key, xpath in selectors.items():
            try:
                if key == "authors" or key == "keywords":
                    elements = driver.find_elements(By.XPATH, xpath)
                    paper[key] = [e.text.strip().rstrip(';；') for e in elements if e.text.strip()]
                else:
                    paper[key] = driver.find_element(By.XPATH, xpath).text.strip()
            except:
                paper[key] = ""
        
        # 获取被引和下载次数
        try:
            paper["cited_count"] = driver.find_element(By.XPATH, '//*[@id="refs"]//a|//div[@class="total-inform"]//span[contains(text(),"被引")]/../em').text.strip()
            paper["download_count"] = driver.find_element(By.XPATH, '//*[@id="DownLoadParts"]//a|//div[@class="total-inform"]//span[contains(text(),"下载")]/../em').text.strip()
        except:
            paper["cited_count"] = paper["download_count"] = "0"

        return paper
    except Exception as e:
        return {"error": str(e), "url": url}
