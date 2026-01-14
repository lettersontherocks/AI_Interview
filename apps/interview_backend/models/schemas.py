"""数据模型定义"""
from pydantic import BaseModel, field_validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class InterviewRound(str, Enum):
    """面试轮次"""
    HR = "HR面"
    TECH_1 = "技术一面"
    TECH_2 = "技术二面"
    DIRECTOR = "总监面"


class InterviewerStyle(str, Enum):
    """面试官风格"""
    FRIENDLY = "friendly"      # 友好型
    PROFESSIONAL = "professional"  # 专业型
    CHALLENGING = "challenging"   # 挑战型
    MENTOR = "mentor"          # 导师型


class InterviewStartRequest(BaseModel):
    """开始面试请求"""
    position_id: str  # 岗位ID（支持父级或子级，如 "backend" 或 "java_backend"）
    position_name: str  # 岗位名称（用于显示）
    round: InterviewRound
    user_id: Optional[str] = None  # 可选：允许未登录用户使用
    resume: Optional[str] = None  # 可选：用户简历
    interviewer_style: Optional[str] = None  # 可选：面试官风格（None时自动选择）

    @field_validator('position_id')
    @classmethod
    def validate_position_id(cls, v: str) -> str:
        """验证岗位ID格式"""
        if not v or len(v) == 0:
            raise ValueError("岗位ID不能为空")
        return v


class InterviewStartResponse(BaseModel):
    """开始面试响应"""
    session_id: str
    question: str
    question_type: str = "开场"
    audio_url: Optional[str] = None  # TTS音频URL


class AnswerRequest(BaseModel):
    """提交回答请求"""
    session_id: str
    answer: str
    finish_interview: bool = False  # 用户是否主动结束面试


class AnswerResponse(BaseModel):
    """回答响应"""
    next_question: Optional[str]
    instant_score: Optional[float]
    hint: Optional[str]
    is_finished: bool = False
    audio_url: Optional[str] = None  # TTS音频URL（预生成）


class InterviewReport(BaseModel):
    """面试报告"""
    session_id: str
    total_score: float
    technical_skill: float  # 技术能力
    communication: float  # 表达能力
    logic_thinking: float  # 逻辑思维
    experience: float  # 项目经验
    suggestions: List[str]  # 改进建议
    transcript: List[dict]  # 对话记录
    created_at: datetime


class UserInfo(BaseModel):
    """用户信息"""
    user_id: str
    openid: str
    nickname: Optional[str]
    avatar: Optional[str]
    is_vip: bool = False
    vip_expire_date: Optional[datetime] = None
    free_count_today: int = 0
    created_at: datetime


class InterviewHistoryItem(BaseModel):
    """面试历史记录项"""
    session_id: str
    position: str
    round: str
    total_score: Optional[float] = None
    is_finished: bool
    created_at: datetime
    finished_at: Optional[datetime] = None


class InterviewSessionDetail(BaseModel):
    """面试会话详情（用于恢复未完成的面试）"""
    session_id: str
    position: str
    round: str
    resume: Optional[str] = None
    transcript: List[dict]  # 对话历史
    current_question: Optional[str] = None
    question_count: int
    is_finished: bool


class WxLoginRequest(BaseModel):
    """微信登录请求"""
    code: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None


class UserRegisterRequest(BaseModel):
    """用户注册请求"""
    openid: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
