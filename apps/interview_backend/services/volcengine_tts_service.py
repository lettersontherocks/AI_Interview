"""火山引擎TTS语音合成服务（豆包）"""
import requests
import json
import os
from typing import Optional


class VolcengineTTSService:
    """火山引擎TTS语音合成服务"""

    def __init__(self, app_id: str = None, access_token: str = None):
        """
        初始化火山引擎TTS服务

        Args:
            app_id: 火山引擎应用ID
            access_token: 火山引擎访问令牌
        """
        self.app_id = app_id or os.getenv("VOLCENGINE_APP_ID")
        self.access_token = access_token or os.getenv("VOLCENGINE_ACCESS_TOKEN")
        self.api_url = "https://openspeech.bytedance.com/api/v1/tts"

        if not self.app_id or not self.access_token:
            print("警告：未配置 VOLCENGINE_APP_ID 或 VOLCENGINE_ACCESS_TOKEN")

    def text_to_speech(
        self,
        text: str,
        voice_type: str = "zh_female_qingxin",
        encoding: str = "mp3",
        speed_ratio: float = 1.0,
        volume_ratio: float = 1.0,
        pitch_ratio: float = 1.0
    ) -> Optional[bytes]:
        """
        文本转语音

        Args:
            text: 要转换的文本
            voice_type: 音色类型
                - zh_female_qingxin: 清新女声（推荐）
                - zh_female_wanwanxiaohe: 湾湾小何（温柔女声）
                - zh_male_chunhouxiaoshu: 淳厚小叔（成熟男声）
                - zh_female_tianmeixiaoyuan: 甜美小媛（甜美女声）
            encoding: 音频格式 (mp3/wav/pcm)
            speed_ratio: 语速 0.5-2.0
            volume_ratio: 音量 0.5-2.0
            pitch_ratio: 音调 0.5-2.0

        Returns:
            音频二进制数据，失败返回None
        """
        try:
            # 构建请求参数
            request_json = {
                "app": {
                    "appid": self.app_id,
                    "token": self.access_token,
                    "cluster": "volcano_tts"
                },
                "user": {
                    "uid": "user_001"
                },
                "audio": {
                    "voice_type": voice_type,
                    "encoding": encoding,
                    "speed_ratio": speed_ratio,
                    "volume_ratio": volume_ratio,
                    "pitch_ratio": pitch_ratio
                },
                "request": {
                    "reqid": f"tts_{os.urandom(8).hex()}",
                    "text": text,
                    "text_type": "plain",
                    "operation": "query"
                }
            }

            # 发送HTTP请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer; {self.access_token}"
            }

            response = requests.post(
                self.api_url,
                headers=headers,
                data=json.dumps(request_json),
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()

                # 检查响应状态
                if result.get("code") == 3000:
                    # 获取音频数据（Base64编码）
                    import base64
                    audio_base64 = result.get("data", "")
                    audio_data = base64.b64decode(audio_base64)

                    print(f"[TTS] 火山引擎合成成功: {len(text)} 字 -> {len(audio_data)} bytes")
                    return audio_data
                else:
                    error_msg = result.get("message", "未知错误")
                    print(f"[TTS] 火山引擎合成失败: {error_msg}")
                    return None
            else:
                print(f"[TTS] HTTP请求失败: {response.status_code}")
                return None

        except Exception as e:
            print(f"[TTS] 火山引擎合成异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def get_available_voices(self) -> dict:
        """
        获取可用的音色列表

        Returns:
            音色信息字典
        """
        return {
            "zh_female_qingxin": {
                "name": "清新女声",
                "description": "清新自然，适合各类场景",
                "gender": "female",
                "style": "professional"
            },
            "zh_female_wanwanxiaohe": {
                "name": "湾湾小何",
                "description": "温柔友善，适合HR面试",
                "gender": "female",
                "style": "friendly"
            },
            "zh_male_chunhouxiaoshu": {
                "name": "淳厚小叔",
                "description": "成熟稳重，适合技术面试",
                "gender": "male",
                "style": "professional"
            },
            "zh_female_tianmeixiaoyuan": {
                "name": "甜美小媛",
                "description": "甜美亲切，适合总监面试",
                "gender": "female",
                "style": "authoritative"
            }
        }


# 全局单例
volcengine_tts_service = None

def get_volcengine_tts_service(app_id: str = None, access_token: str = None) -> VolcengineTTSService:
    """获取火山引擎TTS服务单例"""
    global volcengine_tts_service
    if volcengine_tts_service is None:
        volcengine_tts_service = VolcengineTTSService(app_id, access_token)
    return volcengine_tts_service
