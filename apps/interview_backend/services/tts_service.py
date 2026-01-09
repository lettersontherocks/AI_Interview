"""阿里云TTS语音合成服务"""
import dashscope
from dashscope.audio.tts_v2 import SpeechSynthesizer, AudioFormat
import os
import uuid
from typing import Optional


class TTSService:
    """TTS语音合成服务"""

    def __init__(self, api_key: str = None):
        """
        初始化TTS服务

        Args:
            api_key: DashScope API Key
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if self.api_key:
            dashscope.api_key = self.api_key
        else:
            print("警告：未配置 DASHSCOPE_API_KEY")

    def text_to_speech(
        self,
        text: str,
        voice: str = "longanyang",  # 龙安阳（默认音色）
        format: str = "mp3",
        sample_rate: int = 16000
    ) -> Optional[bytes]:
        """
        文本转语音

        Args:
            text: 要转换的文本
            voice: 音色选择（cosyvoice-v3-flash支持的音色）
                - longanyang: 龙安阳
                - longyingjing_v3: 龙映静v3
            format: 音频格式 (mp3/wav/pcm)
            sample_rate: 采样率 (8000/16000/22050/24000/44100/48000)

        Returns:
            音频二进制数据，失败返回None
        """
        try:
            # 创建语音合成器（使用v3-flash模型，快速且稳定）
            synthesizer = SpeechSynthesizer(
                model="cosyvoice-v3-flash",
                voice=voice
            )

            # 合成音频
            audio_data = synthesizer.call(text)

            if audio_data:
                print(f"[TTS] 合成成功: {len(text)} 字 -> {len(audio_data)} bytes")
                return audio_data
            else:
                print("[TTS] 合成失败: 返回数据为空")
                return None

        except Exception as e:
            print(f"[TTS] 合成失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def save_audio_file(self, audio_data: bytes, filename: str = None) -> Optional[str]:
        """
        保存音频文件到本地

        Args:
            audio_data: 音频二进制数据
            filename: 文件名（不含扩展名），不指定则自动生成

        Returns:
            保存的文件路径，失败返回None
        """
        try:
            if not filename:
                filename = f"tts_{uuid.uuid4().hex[:12]}"

            # 创建音频文件目录
            audio_dir = "data/audio"
            os.makedirs(audio_dir, exist_ok=True)

            # 保存文件
            file_path = os.path.join(audio_dir, f"{filename}.mp3")
            with open(file_path, "wb") as f:
                f.write(audio_data)

            print(f"[TTS] 音频已保存: {file_path}")
            return file_path

        except Exception as e:
            print(f"[TTS] 保存音频失败: {str(e)}")
            return None

    def get_available_voices(self) -> dict:
        """
        获取可用的音色列表

        Returns:
            音色信息字典
        """
        return {
            "longxiaochun": {
                "name": "龙小春（女声）",
                "description": "通用女声，适合各类场景",
                "gender": "female",
                "style": "professional"
            },
            "longxiaojing": {
                "name": "龙小静（女声）",
                "description": "温柔友善，适合HR面试",
                "gender": "female",
                "style": "friendly"
            },
            "longxiaobai": {
                "name": "龙小白（男声）",
                "description": "阳光活力，适合技术面试",
                "gender": "male",
                "style": "professional"
            },
            "longye": {
                "name": "龙爷（男声）",
                "description": "沉稳大气，适合总监面试",
                "gender": "male",
                "style": "authoritative"
            }
        }


# 全局单例
tts_service = None

def get_tts_service(api_key: str = None) -> TTSService:
    """获取TTS服务单例"""
    global tts_service
    if tts_service is None:
        tts_service = TTSService(api_key)
    return tts_service
