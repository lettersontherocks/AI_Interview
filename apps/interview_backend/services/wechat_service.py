"""微信服务 - 处理微信登录"""
import requests
from config import settings


class WechatService:
    """微信小程序服务"""

    def __init__(self):
        self.app_id = settings.wechat_app_id
        self.app_secret = settings.wechat_app_secret

    def code_to_openid(self, code: str) -> dict:
        """
        通过code换取openid和session_key

        Args:
            code: 微信登录凭证

        Returns:
            包含openid和session_key的字典
        """
        # 如果没有配置微信参数，返回模拟数据（开发环境）
        if not self.app_id or not self.app_secret:
            print("警告：未配置微信AppID/AppSecret，返回模拟openid")
            import hashlib
            # 用code生成一个稳定的模拟openid
            mock_openid = f"dev_{hashlib.md5(code.encode()).hexdigest()[:16]}"
            return {
                "openid": mock_openid,
                "session_key": "mock_session_key"
            }

        # 调用微信API
        url = "https://api.weixin.qq.com/sns/jscode2session"
        params = {
            "appid": self.app_id,
            "secret": self.app_secret,
            "js_code": code,
            "grant_type": "authorization_code"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            # 检查错误
            if "errcode" in data and data["errcode"] != 0:
                error_msg = data.get("errmsg", "未知错误")
                raise Exception(f"微信API错误: {error_msg}")

            return {
                "openid": data.get("openid"),
                "session_key": data.get("session_key")
            }
        except Exception as e:
            print(f"微信登录错误: {e}")
            raise Exception(f"微信登录失败: {str(e)}")
