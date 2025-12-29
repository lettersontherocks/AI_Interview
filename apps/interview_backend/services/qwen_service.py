"""通义千问 Qwen API 服务"""
import os
from typing import List, Dict, Optional
import dashscope
from dashscope import Generation


class QwenService:
    """通义千问服务封装"""

    def __init__(self, api_key: str = None):
        """
        初始化 Qwen 服务

        Args:
            api_key: DashScope API Key，如果不提供则从环境变量读取
        """
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if self.api_key:
            dashscope.api_key = self.api_key
        else:
            print("警告：未配置 DASHSCOPE_API_KEY")

    def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "qwen-max",
        system: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.8,
        top_p: float = 0.8,
    ) -> str:
        """
        调用 Qwen 对话 API

        Args:
            messages: 对话消息列表，格式：[{"role": "user", "content": "..."}]
            model: 模型名称，可选: qwen-turbo, qwen-plus, qwen-max, qwen-max-longcontext
            system: 系统提示词（可选）
            max_tokens: 最大生成token数
            temperature: 温度参数，控制随机性 (0-2)
            top_p: 核采样参数 (0-1)

        Returns:
            模型生成的文本内容
        """
        # 如果提供了 system，将其插入到 messages 开头
        if system:
            messages = [{"role": "system", "content": system}] + messages

        try:
            # 调用 DashScope Generation API
            response = Generation.call(
                model=model,
                messages=messages,
                result_format="message",  # 设置输出格式为message
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
            )

            # 检查响应状态
            if response.status_code == 200:
                # 提取生成的文本内容
                content = response.output.choices[0].message.content
                return content
            else:
                error_msg = f"Qwen API 调用失败 - 状态码: {response.status_code}"
                if hasattr(response, 'code'):
                    error_msg += f", 错误码: {response.code}"
                if hasattr(response, 'message'):
                    error_msg += f", 错误信息: {response.message}"

                print(error_msg)
                raise Exception(error_msg)

        except Exception as e:
            print(f"调用 Qwen API 出错: {str(e)}")
            raise Exception(f"调用 Qwen API 失败: {str(e)}")

    def chat_stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "qwen-max",
        system: Optional[str] = None,
        max_tokens: int = 2000,
        temperature: float = 0.8,
        top_p: float = 0.8,
    ):
        """
        调用 Qwen 流式对话 API

        Args:
            参数同 chat() 方法

        Yields:
            流式生成的文本片段
        """
        # 如果提供了 system，将其插入到 messages 开头
        if system:
            messages = [{"role": "system", "content": system}] + messages

        try:
            # 调用流式 API
            responses = Generation.call(
                model=model,
                messages=messages,
                result_format="message",
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                stream=True,  # 启用流式输出
                incremental_output=True,  # 启用增量输出
            )

            # 逐个处理流式响应
            for response in responses:
                if response.status_code == 200:
                    # 提取增量内容
                    content = response.output.choices[0].message.content
                    yield content
                else:
                    error_msg = f"Qwen 流式 API 错误 - 状态码: {response.status_code}"
                    if hasattr(response, 'code'):
                        error_msg += f", 错误码: {response.code}"
                    if hasattr(response, 'message'):
                        error_msg += f", 错误信息: {response.message}"

                    print(error_msg)
                    raise Exception(error_msg)

        except Exception as e:
            print(f"调用 Qwen 流式 API 出错: {str(e)}")
            raise Exception(f"调用 Qwen 流式 API 失败: {str(e)}")

    def get_available_models(self) -> List[str]:
        """
        获取可用的 Qwen 模型列表

        Returns:
            模型名称列表
        """
        return [
            "qwen-turbo",  # 快速响应，适合日常对话
            "qwen-plus",   # 平衡性能和成本，推荐使用
            "qwen-max",    # 最强性能
            "qwen-max-longcontext",  # 支持长文本
        ]
