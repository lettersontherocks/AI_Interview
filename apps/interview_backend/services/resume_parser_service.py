"""简历解析服务 - 混合方案(本地PDF/Word + 阿里云OCR)"""
import os
import io
import re
import fitz  # PyMuPDF
import aiohttp
from docx import Document
from PIL import Image
from typing import Optional
from config import settings


class ResumeParserService:
    """简历解析服务"""

    def __init__(self):
        self.dashscope_api_key = settings.dashscope_api_key
        self.ocr_url = "https://dashscope.aliyuncs.com/api/v1/services/ocr/ocr/ocr_universal"

    async def parse_resume(self, file_content: bytes, filename: str) -> str:
        """
        解析简历文件,返回文本内容

        Args:
            file_content: 文件二进制内容
            filename: 文件名

        Returns:
            提取的文本内容
        """
        file_ext = self._get_file_extension(filename)

        if file_ext == '.pdf':
            return await self._parse_pdf(file_content)
        elif file_ext in ['.doc', '.docx']:
            return self._parse_word(file_content)
        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp']:
            return await self._parse_image(file_content)
        else:
            raise ValueError(f"不支持的文件格式: {file_ext}")

    def _get_file_extension(self, filename: str) -> str:
        """获取文件扩展名"""
        return os.path.splitext(filename.lower())[1]

    async def _parse_pdf(self, file_content: bytes) -> str:
        """
        解析PDF文件
        先尝试提取文字,如果文字少则判定为扫描版,调用OCR
        """
        try:
            # 使用PyMuPDF提取文本
            doc = fitz.open(stream=file_content, filetype="pdf")
            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()

            # 清理文本
            text = self._clean_text(text)

            # 判断是否是扫描版PDF(文字少于50字)
            if len(text.strip()) < 50:
                print("[简历解析] PDF文字少于50字,判定为扫描版,使用OCR")
                return await self._ocr_pdf(file_content)

            print(f"[简历解析] PDF文本提取成功,共{len(text)}字")
            return text

        except Exception as e:
            print(f"[简历解析] PDF解析失败: {e}")
            # 解析失败,降级到OCR
            return await self._ocr_pdf(file_content)

    async def _ocr_pdf(self, file_content: bytes) -> str:
        """使用OCR识别扫描版PDF"""
        # 将PDF转为图片后OCR
        try:
            doc = fitz.open(stream=file_content, filetype="pdf")
            all_text = ""

            for page_num in range(len(doc)):
                page = doc[page_num]
                # 渲染为图片(300 DPI)
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                img_data = pix.tobytes("png")

                # OCR识别
                text = await self._call_aliyun_ocr(img_data)
                all_text += text + "\n"

            doc.close()
            return self._clean_text(all_text)

        except Exception as e:
            print(f"[简历解析] PDF OCR失败: {e}")
            raise ValueError(f"PDF解析失败: {str(e)}")

    def _parse_word(self, file_content: bytes) -> str:
        """解析Word文档"""
        try:
            doc = Document(io.BytesIO(file_content))
            text = "\n".join([para.text for para in doc.paragraphs])

            # 清理文本
            text = self._clean_text(text)

            print(f"[简历解析] Word文档提取成功,共{len(text)}字")
            return text

        except Exception as e:
            print(f"[简历解析] Word解析失败: {e}")
            raise ValueError(f"Word文档解析失败: {str(e)}")

    async def _parse_image(self, file_content: bytes) -> str:
        """解析图片(直接OCR)"""
        try:
            # 验证图片
            Image.open(io.BytesIO(file_content))

            # 调用阿里云OCR
            text = await self._call_aliyun_ocr(file_content)

            print(f"[简历解析] 图片OCR成功,共{len(text)}字")
            return text

        except Exception as e:
            print(f"[简历解析] 图片OCR失败: {e}")
            raise ValueError(f"图片识别失败: {str(e)}")

    async def _call_aliyun_ocr(self, image_data: bytes) -> str:
        """
        调用阿里云OCR API

        文档: https://help.aliyun.com/zh/dashscope/developer-reference/universal-character-recognition
        """
        import base64

        try:
            # 图片转base64
            image_base64 = base64.b64encode(image_data).decode('utf-8')

            # 构建请求
            headers = {
                'Authorization': f'Bearer {self.dashscope_api_key}',
                'Content-Type': 'application/json'
            }

            payload = {
                "model": "ocr-universal-v2",
                "input": {
                    "image": f"data:image/png;base64,{image_base64}"
                }
            }

            # 发送请求
            async with aiohttp.ClientSession() as session:
                async with session.post(self.ocr_url, headers=headers, json=payload, timeout=30) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"[阿里云OCR] 请求失败: {resp.status} - {error_text}")
                        raise ValueError(f"OCR服务错误: {resp.status}")

                    result = await resp.json()

                    # 解析结果
                    if result.get('output') and result['output'].get('results'):
                        text_blocks = result['output']['results']
                        # 提取所有文本块
                        text = "\n".join([block.get('text', '') for block in text_blocks if block.get('text')])
                        return self._clean_text(text)
                    else:
                        print(f"[阿里云OCR] 响应格式异常: {result}")
                        return ""

        except Exception as e:
            print(f"[阿里云OCR] 调用失败: {e}")
            raise ValueError(f"OCR识别失败: {str(e)}")

    def _clean_text(self, text: str) -> str:
        """清理文本(去除多余空白、换行)"""
        if not text:
            return ""

        # 去除多余空白
        text = re.sub(r'\s+', ' ', text)

        # 去除首尾空白
        text = text.strip()

        # 限制长度(最多2000字)
        if len(text) > 2000:
            text = text[:2000]

        return text


# 单例
resume_parser_service = ResumeParserService()
