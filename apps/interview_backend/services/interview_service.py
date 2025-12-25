"""面试服务逻辑"""
import requests
import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import flag_modified

from database.db import InterviewSession, InterviewReport, User
from models.schemas import (
    InterviewStartRequest, InterviewStartResponse,
    AnswerRequest, AnswerResponse, InterviewReport as InterviewReportSchema
)
from config import settings


class InterviewService:
    """面试服务"""

    def __init__(self, claude_api_url: str = None):
        self.claude_api_url = claude_api_url or settings.claude_api_url

    def _call_claude(self, messages: List[dict], system: str = None, temperature: float = 0.8) -> str:
        """调用Claude API"""
        data = {
            "messages": messages,
            "max_tokens": 2000,
            "temperature": temperature
        }
        if system:
            data["system"] = system

        try:
            response = requests.post(self.claude_api_url, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result.get("content", "")
        except Exception as e:
            raise Exception(f"调用Claude API失败: {str(e)}")

    def _get_system_prompt(self, position: str, round: str, resume: Optional[str] = None) -> str:
        """生成系统提示词"""
        base_prompt = f"""你是一位经验丰富的{position}面试官，正在进行{round}。

面试要求：
1. 提问要专业、有针对性，根据候选人的回答深入追问
2. 问题难度要循序渐进，从基础到进阶
3. 关注候选人的技术深度、项目经验、逻辑思维和沟通能力
4. 每次只问一个问题，等待候选人回答后再继续
5. 根据候选人的回答给出即时评分（0-10分）和简短提示

面试流程：
- 开场：简单自我介绍和热身问题（1-2个）
- 基础知识：考察核心技术栈（2-3个）
- 深入探讨：项目经验和解决方案（2-3个）
- 场景问题：实际问题解决能力（1-2个）
- 收尾：候选人提问环节

总计8-10个问题，控制在15-20分钟内。"""

        if resume:
            base_prompt += f"\n\n候选人简历信息：\n{resume}\n\n请根据简历内容针对性提问。"

        return base_prompt

    def _get_position_questions(self, position: str) -> str:
        """获取岗位相关问题提示"""
        questions_guide = {
            "前端工程师": "重点考察：HTML/CSS/JavaScript、React/Vue等框架、性能优化、工程化、浏览器原理",
            "后端工程师": "重点考察：编程语言（Python/Java/Go）、数据库、缓存、消息队列、微服务、系统设计",
            "产品经理": "重点考察：产品思维、需求分析、用户研究、数据分析、项目管理、沟通协调",
            "算法工程师": "重点考察：机器学习/深度学习算法、数学基础、模型优化、工程实现、论文理解",
            "数据分析师": "重点考察：SQL、Python/R、统计学、数据可视化、业务理解、A/B测试",
            "销售": "重点考察：销售经验、客户关系、谈判技巧、目标达成、行业理解",
            "市场运营": "重点考察：运营策略、数据分析、用户增长、活动策划、内容运营"
        }
        return questions_guide.get(position, "")

    def start_interview(self, request: InterviewStartRequest, db: Session) -> InterviewStartResponse:
        """开始面试"""
        # 生成会话ID
        session_id = f"session_{uuid.uuid4().hex[:16]}"

        # 生成系统提示词
        system_prompt = self._get_system_prompt(request.position, request.round, request.resume)
        questions_guide = self._get_position_questions(request.position)

        # 生成开场问题
        messages = [
            {
                "role": "user",
                "content": f"""现在开始{request.position}的{request.round}。

{questions_guide}

请提出第一个开场问题，要求：
1. 友好、专业的开场白
2. 一个简单的热身问题
3. 让候选人放松并进入状态

直接输出问题，不要输出其他内容。"""
            }
        ]

        first_question = self._call_claude(messages, system=system_prompt, temperature=0.7)

        # 创建会话记录
        session = InterviewSession(
            session_id=session_id,
            user_id=request.user_id,
            position=request.position,
            round=request.round,
            resume=request.resume,
            current_question=first_question,
            question_count=1,
            transcript=[
                {
                    "role": "interviewer",
                    "content": first_question,
                    "timestamp": datetime.utcnow().isoformat(),
                    "question_number": 1
                }
            ]
        )
        db.add(session)
        db.commit()

        return InterviewStartResponse(
            session_id=session_id,
            question=first_question,
            question_type="开场"
        )

    def process_answer(self, request: AnswerRequest, db: Session) -> AnswerResponse:
        """处理候选人回答"""
        # 获取会话
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == request.session_id
        ).first()

        if not session:
            raise ValueError("会话不存在")

        if session.is_finished:
            raise ValueError("面试已结束")

        # 记录候选人回答
        session.transcript.append({
            "role": "candidate",
            "content": request.answer,
            "timestamp": datetime.utcnow().isoformat(),
            "question_number": session.question_count
        })
        flag_modified(session, "transcript")

        # 构建对话历史
        messages = []
        for item in session.transcript[-6:]:  # 最近3轮对话
            role = "assistant" if item["role"] == "interviewer" else "user"
            messages.append({"role": role, "content": item["content"]})

        # 判断是否继续面试（8-10个问题）
        should_continue = session.question_count < 10

        if should_continue:
            # 生成下一个问题
            system_prompt = self._get_system_prompt(session.position, session.round, session.resume)
            messages.append({
                "role": "user",
                "content": f"""候选人已回答问题{session.question_count}。

请执行以下任务：
1. 对候选人的回答进行评分（0-10分）
2. 给出简短的即时反馈或提示（1-2句话）
3. 提出下一个问题（第{session.question_count + 1}个问题）

要求：
- 根据候选人回答质量调整问题难度
- 如果回答不够深入，可以追问
- 如果回答很好，可以提升难度
- 确保问题多样性，不要重复

请按以下JSON格式输出：
{{
    "score": 8.5,
    "hint": "回答不错，但可以更深入",
    "next_question": "下一个问题内容"
}}"""
            })

            response_text = self._call_claude(messages, system=system_prompt, temperature=0.8)

            # 解析响应
            try:
                # 尝试提取JSON
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                else:
                    response_data = json.loads(response_text)

                instant_score = response_data.get("score", 7.0)
                hint = response_data.get("hint", "")
                next_question = response_data.get("next_question", "")
            except:
                # 如果解析失败，使用默认值
                instant_score = 7.0
                hint = ""
                next_question = response_text

            # 更新最后一条候选人回答的评分
            session.transcript[-1]["score"] = instant_score
            session.transcript[-1]["hint"] = hint

            # 记录下一个问题
            session.question_count += 1
            session.current_question = next_question
            session.transcript.append({
                "role": "interviewer",
                "content": next_question,
                "timestamp": datetime.utcnow().isoformat(),
                "question_number": session.question_count
            })
            flag_modified(session, "transcript")

            db.commit()

            return AnswerResponse(
                next_question=next_question,
                instant_score=instant_score,
                hint=hint,
                is_finished=False
            )
        else:
            # 面试结束
            session.is_finished = True
            session.finished_at = datetime.utcnow()
            db.commit()

            # 生成报告
            report = self.generate_report(request.session_id, db)

            return AnswerResponse(
                next_question=None,
                instant_score=None,
                hint="面试已结束，感谢您的参与！",
                is_finished=True
            )

    def generate_report(self, session_id: str, db: Session) -> InterviewReportSchema:
        """生成面试报告"""
        # 获取会话
        session = db.query(InterviewSession).filter(
            InterviewSession.session_id == session_id
        ).first()

        if not session:
            raise ValueError("会话不存在")

        # 检查是否已有报告
        existing_report = db.query(InterviewReport).filter(
            InterviewReport.session_id == session_id
        ).first()

        if existing_report:
            return InterviewReportSchema(
                session_id=existing_report.session_id,
                total_score=existing_report.total_score,
                technical_skill=existing_report.technical_skill,
                communication=existing_report.communication,
                logic_thinking=existing_report.logic_thinking,
                experience=existing_report.experience,
                suggestions=existing_report.suggestions,
                transcript=existing_report.transcript,
                created_at=existing_report.created_at
            )

        # 使用Claude分析面试表现
        system_prompt = f"""你是一位专业的{session.position}面试评估专家。
请根据以下面试对话记录，生成详细的面试评估报告。"""

        transcript_text = "\n\n".join([
            f"{'面试官' if item['role'] == 'interviewer' else '候选人'}: {item['content']}"
            for item in session.transcript
        ])

        messages = [{
            "role": "user",
            "content": f"""面试记录：

{transcript_text}

请对候选人的表现进行全面评估，并按以下JSON格式输出：

{{
    "total_score": 85.5,
    "technical_skill": 88.0,
    "communication": 82.0,
    "logic_thinking": 86.0,
    "experience": 85.0,
    "suggestions": [
        "建议1",
        "建议2",
        "建议3"
    ]
}}

评分标准（0-100分）：
- technical_skill: 技术能力，专业知识深度和广度
- communication: 表达能力，逻辑清晰度和沟通效果
- logic_thinking: 逻辑思维，问题分析和解决能力
- experience: 项目经验，实践经验和应用能力
- total_score: 综合评分

suggestions要包含3-5条具体的改进建议。"""
        }]

        response_text = self._call_claude(messages, system=system_prompt, temperature=0.5)

        # 解析报告
        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                report_data = json.loads(json_match.group())
            else:
                report_data = json.loads(response_text)
        except:
            # 默认评分
            report_data = {
                "total_score": 75.0,
                "technical_skill": 75.0,
                "communication": 75.0,
                "logic_thinking": 75.0,
                "experience": 75.0,
                "suggestions": ["继续加强技术学习", "提升表达能力", "积累项目经验"]
            }

        # 保存报告
        report = InterviewReport(
            session_id=session_id,
            user_id=session.user_id,
            total_score=report_data["total_score"],
            technical_skill=report_data["technical_skill"],
            communication=report_data["communication"],
            logic_thinking=report_data["logic_thinking"],
            experience=report_data["experience"],
            suggestions=report_data["suggestions"],
            transcript=session.transcript
        )
        db.add(report)
        db.commit()

        return InterviewReportSchema(
            session_id=session_id,
            total_score=report_data["total_score"],
            technical_skill=report_data["technical_skill"],
            communication=report_data["communication"],
            logic_thinking=report_data["logic_thinking"],
            experience=report_data["experience"],
            suggestions=report_data["suggestions"],
            transcript=session.transcript,
            created_at=report.created_at
        )
