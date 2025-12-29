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
from services.position_service import position_service
from services.resume_parser_service import resume_parser_service
from config import settings
from datetime import datetime, date

router = APIRouter()
interview_service = InterviewService()
asr_service = ASRService()
wechat_service = WechatService()


@router.get("/positions")
async def get_positions():
    """获取所有岗位分类和岗位列表"""
    return position_service.get_all_categories()


@router.get("/positions/search")
async def search_positions(keyword: str):
    """根据关键词搜索岗位"""
    if not keyword or len(keyword.strip()) == 0:
        raise HTTPException(status_code=400, detail="搜索关键词不能为空")
    return position_service.search_positions(keyword.strip())


@router.post("/resume/parse")
async def parse_resume(file: UploadFile = File(...)):
    """
    解析简历文件
    支持: PDF、Word(doc/docx)、图片(jpg/png)
    """
    print(f"[简历上传] 收到文件: {file.filename}, 类型: {file.content_type}")

    # 检查文件大小(限制10MB)
    file_content = await file.read()
    file_size_mb = len(file_content) / (1024 * 1024)

    if file_size_mb > 10:
        raise HTTPException(status_code=400, detail=f"文件过大({file_size_mb:.1f}MB),最大支持10MB")

    # 检查文件格式
    allowed_extensions = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png', '.bmp']
    file_ext = os.path.splitext(file.filename.lower())[1]

    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件格式: {file_ext}。支持格式: {', '.join(allowed_extensions)}"
        )

    try:
        # 解析简历
        text = await resume_parser_service.parse_resume(file_content, file.filename)

        if not text or len(text.strip()) == 0:
            raise HTTPException(status_code=400, detail="未能从文件中提取到文字内容")

        print(f"[简历上传] 解析成功,提取{len(text)}字")

        return {
            "success": True,
            "text": text,
            "length": len(text)
        }

    except ValueError as e:
        print(f"[简历上传] 解析失败: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[简历上传] 未知错误: {e}")
        raise HTTPException(status_code=500, detail="简历解析失败,请稍后重试")


@router.get("/interview/start")
async def start_interview_get_debug():
    """调试用：记录 GET 请求"""
    print("[DEBUG] 收到 GET 请求到 /interview/start - 这是错误的！应该使用 POST")
    raise HTTPException(status_code=405, detail="请使用 POST 方法。GET 请求不被支持。请检查小程序代码是否正确设置了 method: 'POST'")


@router.post("/interview/start", response_model=InterviewStartResponse)
async def start_interview(request: InterviewStartRequest, db: Session = Depends(get_db)):
    """开始面试"""
    try:
        print(f"[DEBUG] 收到开始面试请求: position_id={request.position_id}, position_name={request.position_name}, round={request.round}")

        # 验证岗位ID有效性
        if not position_service.validate_position_id(request.position_id):
            raise HTTPException(status_code=400, detail=f"无效的岗位ID: {request.position_id}")

        # 检查用户配额（仅对已登录用户）
        user = None
        if request.user_id:
            user = db.query(User).filter(User.user_id == request.user_id).first()

            if user:
                # 检查今日免费次数（统一使用 UTC 时间进行日期比较）
                today_utc = datetime.utcnow().date()
                if user.last_free_date and user.last_free_date.date() == today_utc:
                    if user.free_count_today >= settings.free_daily_limit and not user.is_vip:
                        raise HTTPException(status_code=403, detail="今日免费次数已用完，请购买会员或单次面试")
                else:
                    # 重置今日计数
                    user.free_count_today = 0
                    user.last_free_date = datetime.utcnow()
                    db.commit()  # 立即提交重置，避免后续异常导致未保存

        print(f"[DEBUG] 开始调用 interview_service.start_interview")
        # 开始面试（允许未登录用户，如果没有指定风格则自动选择）
        response = interview_service.start_interview(
            request,
            db,
            interviewer_style=request.interviewer_style  # None时会自动选择
        )
        print(f"[DEBUG] interview_service.start_interview 返回成功")

        # 更新免费次数（仅对已登录用户）
        if user and not user.is_vip:
            user.free_count_today += 1
            db.commit()

        print(f"[DEBUG] 准备返回响应: session_id={response.session_id}")
        return response
    except HTTPException:
        # HTTPException 直接向上抛出，不做处理
        raise
    except ValueError as e:
        print(f"[ERROR] ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"[ERROR] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")


@router.post("/interview/answer", response_model=AnswerResponse)
async def submit_answer(request: AnswerRequest, db: Session = Depends(get_db)):
    """提交回答"""
    try:
        print(f"收到回答请求 - session_id: {request.session_id}, answer长度: {len(request.answer)}")
        response = interview_service.process_answer(request, db)
        return response
    except ValueError as e:
        print(f"ValueError in submit_answer: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Exception in submit_answer: {str(e)}")
        import traceback
        traceback.print_exc()
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
        import tempfile
        import time

        # 使用系统临时目录
        temp_dir = tempfile.gettempdir()
        temp_filename = f"voice_{int(time.time())}.mp3"
        temp_path = os.path.join(temp_dir, temp_filename)

        with open(temp_path, 'wb') as f:
            f.write(audio_data)

        try:
            # 调用ASR服务识别
            text = asr_service.recognize(temp_path)
            return {"text": text}
        finally:
            # 识别完成后删除临时文件
            if os.path.exists(temp_path):
                os.remove(temp_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"语音识别失败: {str(e)}")
