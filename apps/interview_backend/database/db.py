"""数据库模型定义"""
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ai_interview.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    """用户表"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), unique=True, index=True, nullable=False)
    openid = Column(String(100), unique=True, nullable=False)
    nickname = Column(String(100))
    avatar = Column(String(500))
    is_vip = Column(Boolean, default=False)
    vip_expire_date = Column(DateTime)
    free_count_today = Column(Integer, default=0)
    last_free_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InterviewSession(Base):
    """面试会话表"""
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), index=True, nullable=False)
    position = Column(String(50), nullable=False)  # 岗位类型
    round = Column(String(50), nullable=False)  # 面试轮次
    resume = Column(Text)  # 简历
    transcript = Column(JSON, default=list)  # 对话记录 [{role, content, timestamp, score}]
    current_question = Column(Text)  # 当前问题
    question_count = Column(Integer, default=0)  # 已提问数量
    is_finished = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)


class InterviewReport(Base):
    """面试报告表"""
    __tablename__ = "interview_reports"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), index=True, nullable=False)
    total_score = Column(Float)  # 总分
    technical_skill = Column(Float)  # 技术能力
    communication = Column(Float)  # 表达能力
    logic_thinking = Column(Float)  # 逻辑思维
    experience = Column(Float)  # 项目经验
    suggestions = Column(JSON, default=list)  # 改进建议
    transcript = Column(JSON, default=list)  # 完整对话记录
    created_at = Column(DateTime, default=datetime.utcnow)


class Payment(Base):
    """支付记录表"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(String(50), index=True, nullable=False)
    payment_type = Column(String(20), nullable=False)  # vip_monthly, single_interview
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending, paid, failed
    transaction_id = Column(String(100))  # 微信支付交易号
    created_at = Column(DateTime, default=datetime.utcnow)
    paid_at = Column(DateTime)


def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
