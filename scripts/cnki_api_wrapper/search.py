import httpx
from auth import CNKIAuth

class CNKIOpenXSearch:
    """知网 OpenX 搜索接口封装"""
    
    SEARCH_URL = "https://api.cn-ki.net/openapi/search"

    def __init__(self, auth: CNKIAuth):
        self.auth = auth

    def search(self, keyword: str, db: str = "SCAD", sort_type: str = "relevance"):
        """执行搜索
        :param keyword: 检索关键字
        :param db: 目标数据库 (默认 SCAD)
        :param sort_type: 排序方式
        """
        headers = {
            "Authorization": f"Bearer {self.auth.get_token()}"
        }
        params = {
            "keyword": keyword,
            "db": db,
            "sort_type": sort_type
        }
        
        response = httpx.get(self.SEARCH_URL, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

if __name__ == "__main__":
    # 使用示例需要填入真实凭据
    pass
