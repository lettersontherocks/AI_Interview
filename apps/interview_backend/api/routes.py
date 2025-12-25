"""API路由"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import base64
import os
import tempfile

from database.db import get_db, User, InterviewSession, InterviewReport as DBReport
from models.schemas import (
    InterviewStartRequest, InterviewStartResponse,
    AnswerRequest, AnswerResponse,
    InterviewReport, UserInfo, InterviewHistoryItem, InterviewSessionDetail,
    WxLoginRequest, UserRegisterRequest
)
from services.interview_service import InterviewService
from services.asr_service import ASRService
from services.wechat_service import WechatService
from config import settings
from datetime import datetime, date

router = APIRouter()
interview_service = InterviewService()
asr_service = ASRService()
wechat_service = WechatService()


@router.post("/interview/start", response_model=InterviewStartResponse)
async def start_interview(request: InterviewStartRequest, db: Session = Depends(get_db)):
    """开始面试"""
    try:
        # 检查用户配额
        user = db.query(User).filter(User.user_id == request.user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 检查今日免费次数
        today = date.today()
        if user.last_free_date and user.last_free_date.date() == today:
            if user.free_count_today >= settings.free_daily_limit and not user.is_vip:
                raise HTTPException(status_code=403, detail="今日免费次数已用完，请购买会员或单次面试")
        else:
            # 重置今日计数
            user.free_count_today = 0
            user.last_free_date = datetime.utcnow()

        # 开始面试
        response = interview_service.start_interview(request, db)

        # 更新免费次数
        if not user.is_vip:
            user.free_count_today += 1
        db.commit()

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/interview/answer", response_model=AnswerResponse)
async def submit_answer(request: AnswerRequest, db: Session = Depends(get_db)):
    """提交回答"""
    try:
        response = interview_service.process_answer(request, db)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/interview/report/{session_id}", response_model=InterviewReport)
async def get_report(session_id: str, db: Session = Depends(get_db)):
    """获取面试报告"""
    try:
        report = interview_service.generate_report(session_id, db)
        return report
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/user/wx-login", response_model=UserInfo)
async def wx_login(request: WxLoginRequest, db: Session = Depends(get_db)):
    """微信登录 - 通过code换取openid并注册/登录用户"""
    try:
        # 调用微信服务换取openid
        wx_data = wechat_service.code_to_openid(request.code)
        openid = wx_data.get("openid")

        if not openid:
            raise HTTPException(status_code=400, detail="获取openid失败")

        # 检查用户是否存在
        existing_user = db.query(User).filter(User.openid == openid).first()
        if existing_user:
            # 用户已存在，更新昵称和头像
            if request.nickname:
                existing_user.nickname = request.nickname
            if request.avatar:
                existing_user.avatar = request.avatar
            db.commit()
            db.refresh(existing_user)

            return UserInfo(
                user_id=existing_user.user_id,
                openid=existing_user.openid,
                nickname=existing_user.nickname,
                avatar=existing_user.avatar,
                is_vip=existing_user.is_vip,
                vip_expire_date=existing_user.vip_expire_date,
                free_count_today=existing_user.free_count_today,
                created_at=existing_user.created_at
            )

        # 创建新用户
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:16]}"
        user = User(
            user_id=user_id,
            openid=openid,
            nickname=request.nickname or "微信用户",
            avatar=request.avatar or ""
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return UserInfo(
            user_id=user.user_id,
            openid=user.openid,
            nickname=user.nickname,
            avatar=user.avatar,
            is_vip=user.is_vip,
            vip_expire_date=user.vip_expire_date,
            free_count_today=user.free_count_today,
            created_at=user.created_at
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"登录失败: {str(e)}")


@router.post("/user/register", response_model=UserInfo)
async def register_user(request: UserRegisterRequest, db: Session = Depends(get_db)):
    """用户注册（简化版，不需要微信授权）"""
    try:
        # 检查用户是否存在
        existing_user = db.query(User).filter(User.openid == request.openid).first()
        if existing_user:
            return UserInfo(
                user_id=existing_user.user_id,
                openid=existing_user.openid,
                nickname=existing_user.nickname,
                avatar=existing_user.avatar,
                is_vip=existing_user.is_vip,
                vip_expire_date=existing_user.vip_expire_date,
                free_count_today=existing_user.free_count_today,
                created_at=existing_user.created_at
            )

        # 创建新用户
        import uuid
        user_id = f"user_{uuid.uuid4().hex[:16]}"
        user = User(
            user_id=user_id,
            openid=request.openid,
            nickname=request.nickname or "用户",
            avatar=request.avatar or ""
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        return UserInfo(
            user_id=user.user_id,
            openid=user.openid,
            nickname=user.nickname,
            avatar=user.avatar,
            is_vip=user.is_vip,
            vip_expire_date=user.vip_expire_date,
            free_count_today=user.free_count_today,
            created_at=user.created_at
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.get("/user/{user_id}", response_model=UserInfo)
async def get_user_info(user_id: str, db: Session = Depends(get_db)):
    """获取用户信息"""
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    return UserInfo(
        user_id=user.user_id,
        openid=user.openid,
        nickname=user.nickname,
        avatar=user.avatar,
        is_vip=user.is_vip,
        vip_expire_date=user.vip_expire_date,
        free_count_today=user.free_count_today,
        created_at=user.created_at
    )


@router.get("/user/{user_id}/history", response_model=List[InterviewHistoryItem])
async def get_user_history(user_id: str, db: Session = Depends(get_db)):
    """获取用户面试历史记录"""
    # 验证用户存在
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 查询用户的所有面试会话，按创建时间倒序
    sessions = db.query(InterviewSession).filter(
        InterviewSession.user_id == user_id
    ).order_by(InterviewSession.created_at.desc()).all()

    # 构建历史记录列表
    history = []
    for session in sessions:
        # 尝试获取对应的报告以获取总分
        report = db.query(DBReport).filter(
            DBReport.session_id == session.session_id
        ).first()

        history.append(InterviewHistoryItem(
            session_id=session.session_id,
            position=session.position,
            round=session.round,
            total_score=report.total_score if report else None,
            is_finished=session.is_finished,
            created_at=session.created_at,
            finished_at=session.finished_at
        ))

    return history


@router.get("/interview/session/{session_id}", response_model=InterviewSessionDetail)
async def get_session_detail(session_id: str, db: Session = Depends(get_db)):
    """获取面试会话详情（用于恢复未完成的面试）"""
    session = db.query(InterviewSession).filter(
        InterviewSession.session_id == session_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="会话不存在")

    return InterviewSessionDetail(
        session_id=session.session_id,
        position=session.position,
        round=session.round,
        resume=session.resume,
        transcript=session.transcript or [],
        current_question=session.current_question,
        question_count=session.question_count,
        is_finished=session.is_finished
    )


@router.post("/voice/recognize")
async def recognize_voice(audio: UploadFile = File(...)):
    """语音识别接口"""
    try:
        # 读取上传的音频文件
        audio_data = await audio.read()

        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
            temp_file.write(audio_data)
            temp_path = temp_file.name

        try:
            # 调用ASR服务识别
            text = asr_service.recognize(temp_path)

            return {"text": text}
        finally:
            # 删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音识别失败: {str(e)}")
