import time
import httpx
import jwt
from typing import Optional

class CNKIAuth:
    """知网 OpenX API 认证封装"""
    
    GATEWAY_URL = "https://gateway.cnki.net/openx/oauth2/token"

    def __init__(self, app_id: str, api_key: str, secret_key: str):
        self.app_id = app_id
        self.api_key = api_key
        self.secret_key = secret_key
        self._token: Optional[str] = None
        self._expires_at: float = 0

    def get_token(self) -> str:
        """获取有效的 JWT Token"""
        if self._token and time.time() < self._expires_at:
            return self._token
        
        return self._refresh_token()

    def _refresh_token(self) -> str:
        """从官方网关刷新 Token"""
        # 注意：此处具体的 OAuth2 流程需根据知网官方文档的模式（Client Credentials / Auth Code）细化
        # 以下为基于 AppId 和 SecretKey 的典型客户端模式示例
        payload = {
            "grant_type": "client_credentials",
            "client_id": self.app_id,
            "client_secret": self.secret_key
        }
        
        response = httpx.post(self.GATEWAY_URL, data=payload)
        response.raise_for_status()
        
        data = response.json()
        self._token = data["access_token"]
        # 默认有效期 2 小时，提前 5 分钟刷新
        self._expires_at = time.time() + data.get("expires_in", 7200) - 300
        
        return self._token

if __name__ == "__main__":
    # 使用示例
    auth = CNKIAuth(
        app_id="YOUR_APP_ID",
        api_key="YOUR_API_KEY",
        secret_key="YOUR_SECRET_KEY"
    )
    print("准备获取 Token...")
