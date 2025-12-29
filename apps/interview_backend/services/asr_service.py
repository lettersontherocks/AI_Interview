"""语音识别服务 - 阿里云ASR"""
import dashscope
from dashscope.audio.asr import Recognition
from config import settings
import os


class ASRService:
    """阿里云语音识别服务"""

    def __init__(self):
        # 从配置文件读取阿里云API Key
        if settings.dashscope_api_key:
            dashscope.api_key = settings.dashscope_api_key
        else:
            print("警告：未配置 dashscope_api_key")

    def recognize(self, audio_file_path: str) -> str:
        """
        识别音频文件

        Args:
            audio_file_path: 音频文件路径

        Returns:
            识别的文本
        """
        # 如果没有配置API Key，返回模拟数据（用于开发测试）
        if not dashscope.api_key:
            print("警告：未配置阿里云ASR，返回模拟数据")
            return self._mock_recognize(audio_file_path)

        try:
            print(f"开始识别音频文件: {audio_file_path}")

            # 检查文件是否存在
            if not os.path.exists(audio_file_path):
                raise Exception(f"音频文件不存在: {audio_file_path}")

            file_size = os.path.getsize(audio_file_path)
            print(f"音频文件大小: {file_size} bytes")

            # 检测音频格式（微信开发者工具可能返回webm而不是mp3）
            # 读取文件头部来判断格式
            with open(audio_file_path, 'rb') as f:
                header = f.read(12)

            # WebM文件头: 1A 45 DF A3
            # MP3文件头: FF FB 或 FF F3 或 FF F2 或 ID3
            is_webm = header[:4] == b'\x1a\x45\xdf\xa3'
            is_mp3 = (header[:2] in [b'\xff\xfb', b'\xff\xf3', b'\xff\xf2'] or
                     header[:3] == b'ID3')

            if is_webm:
                audio_format = 'opus'  # WebM通常使用opus编码
                print("检测到WebM格式，使用opus格式识别")
            elif is_mp3:
                audio_format = 'mp3'
                print("检测到MP3格式，使用mp3格式识别")
            else:
                # 默认尝试mp3
                audio_format = 'mp3'
                print(f"未知格式(header: {header[:4].hex()})，默认使用mp3格式识别")

            # 创建 Recognition 实例并调用
            recognition = Recognition(
                model='paraformer-realtime-v2',
                format=audio_format,
                sample_rate=16000,
                callback=None
            )

            # 调用实时语音识别 API（传入文件路径）
            print(f"调用ASR API，文件路径: {audio_file_path}")
            result = recognition.call(audio_file_path)

            print(f"ASR调用完成，状态码: {result.status_code}")
            print(f"完整结果: {result}")

            # 解析识别结果
            if result.status_code == 200:
                # 从 result.output 提取文本
                if hasattr(result, 'output') and result.output:
                    print(f"result.output: {result.output}")

                    # 方式1: output['sentence'][0]['text'] (数组格式)
                    if isinstance(result.output, dict):
                        if 'sentence' in result.output:
                            sentence = result.output['sentence']
                            # sentence 是数组
                            if isinstance(sentence, list) and len(sentence) > 0:
                                if isinstance(sentence[0], dict) and 'text' in sentence[0]:
                                    text = sentence[0]['text']
                                    print(f"ASR识别结果: {text}")
                                    return text
                            # sentence 是字典
                            elif isinstance(sentence, dict) and 'text' in sentence:
                                text = sentence['text']
                                print(f"ASR识别结果: {text}")
                                return text

                        # 方式2: output['text']
                        if 'text' in result.output:
                            text = result.output['text']
                            print(f"ASR识别结果（方式2）: {text}")
                            return text

                print("警告：ASR返回结果为空")
                print(f"详细信息 - output: {result.output if hasattr(result, 'output') else 'No output'}")
                return self._mock_recognize(audio_file_path)
            else:
                error_msg = f"ASR识别失败，状态码: {result.status_code}"
                print(error_msg)
                if hasattr(result, 'message'):
                    print(f"错误信息: {result.message}")
                raise Exception(error_msg)

        except Exception as e:
            print(f"ASR识别错误: {e}")
            import traceback
            traceback.print_exc()
            # 开发环境下降级到模拟数据，避免影响测试
            return self._mock_recognize(audio_file_path)

    def _mock_recognize(self, audio_file_path: str) -> str:
        """模拟识别（开发测试用）"""
        # 提示用户重新录音
        return "无法识别，请您重新回答！"
