"""面试服务逻辑"""
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
from services.qwen_service import QwenService
from services.position_service import position_service
from services.knowledge_service import knowledge_service


class InterviewService:
    """面试服务"""

    def __init__(self):
        # 初始化 Qwen 服务
        self.qwen_service = QwenService(api_key=settings.dashscope_api_key)

    def _call_llm(self, messages: List[dict], system: str = None, temperature: float = 0.8) -> str:
        """调用大模型 API（使用 Qwen）"""
        try:
            return self.qwen_service.chat(
                messages=messages,
                system=system,
                temperature=temperature,
                max_tokens=2000
            )
        except Exception as e:
            raise Exception(f"调用 Qwen API 失败: {str(e)}")

    def _auto_select_interviewer_style(self, round: str) -> str:
        """根据面试轮次智能选择面试官风格"""
        import random

        # 根据面试轮次设定可能的风格组合，模拟真实场景
        style_mapping = {
            "HR面": ["friendly", "mentor"],  # HR更倾向友好和引导
            "技术一面": ["friendly", "professional"],  # 基础面试，友好或专业
            "技术二面": ["professional", "challenging"],  # 深度面试，专业或有压力
            "总监面": ["professional", "challenging", "mentor"]  # 高层面试，各种可能
        }

        candidates = style_mapping.get(round, ["friendly", "professional"])
        selected = random.choice(candidates)

        print(f"[面试官分配] {round} -> 自动选择: {selected}")
        return selected

    def _extract_tech_keywords(self, answer: str) -> str:
        """从候选人回答中提取技术关键词

        Args:
            answer: 候选人回答

        Returns:
            提取的关键词字符串
        """
        # 简单实现：提取常见技术词汇
        # 可以使用更复杂的 NLP 方法，但这里保持简单
        import re

        # 常见技术词汇模式（中英文）
        tech_patterns = [
            r'\b[A-Z][a-z]+(?:[A-Z][a-z]+)*\b',  # 驼峰命名（如：ArrayList, HashMap）
            r'\b[A-Z]{2,}\b',  # 全大写缩写（如：API, HTTP, SQL）
            r'\b(?:Python|Java|JavaScript|React|Vue|Django|Flask|Redis|MySQL|MongoDB|Docker|Kubernetes|Git)\b',  # 常见技术栈
            r'[\u4e00-\u9fa5]{2,}(?:算法|模式|协议|框架|库|方法|函数|类|接口)',  # 中文技术词
        ]

        keywords = set()
        for pattern in tech_patterns:
            matches = re.findall(pattern, answer)
            keywords.update(matches)

        # 限制关键词数量，避免查询过长
        keywords_list = list(keywords)[:5]
        return " ".join(keywords_list) if keywords_list else ""

    def _get_interviewer_style(self, style: str = "friendly") -> dict:
        """获取面试官风格配置"""
        styles = {
            "friendly": {
                "name": "友好型",
                "description": "温和友善，鼓励性强，适合缓解紧张",
                "personality": "你是一位温和友善的面试官，善于鼓励候选人，营造轻松氛围。",
                "feedback_examples": ["很好！", "不错的回答", "我明白了", "嗯，继续说", "很有意思"]
            },
            "professional": {
                "name": "专业型",
                "description": "严谨专业，注重深度，追求技术细节",
                "personality": "你是一位严谨专业的技术专家，注重技术深度和细节，善于深入追问。",
                "feedback_examples": ["好的", "明白", "继续", "嗯", "我了解了"]
            },
            "challenging": {
                "name": "挑战型",
                "description": "有压力感，善于提出尖锐问题",
                "personality": "你是一位经验丰富的高级面试官，善于通过挑战性问题考察候选人的应变能力和深度思考。",
                "feedback_examples": ["有意思", "这个答案还不够深入", "继续", "然后呢", "还有吗"]
            },
            "mentor": {
                "name": "导师型",
                "description": "像导师一样引导，善于启发思考",
                "personality": "你是一位像导师一样的面试官，善于通过引导和启发帮助候选人展现最佳状态。",
                "feedback_examples": ["很好，我们换个角度想想", "不错的思路", "明白了", "有道理", "继续深入说说"]
            }
        }
        return styles.get(style, styles["friendly"])

    def get_all_interviewer_styles(self) -> List[Dict]:
        """获取所有面试官风格（供前端选择）"""
        styles_config = {
            "friendly": {
                "name": "友好型",
                "description": "温和友善，鼓励性强，适合缓解紧张",
                "icon": "😊"
            },
            "professional": {
                "name": "专业型",
                "description": "严谨专业，注重深度，追求技术细节",
                "icon": "💼"
            },
            "challenging": {
                "name": "挑战型",
                "description": "有压力感，善于提出尖锐问题",
                "icon": "🔥"
            },
            "mentor": {
                "name": "导师型",
                "description": "像导师一样引导，善于启发思考",
                "icon": "🎓"
            }
        }

        result = []
        for style_id, config in styles_config.items():
            result.append({
                "id": style_id,
                "name": config["name"],
                "description": config["description"],
                "icon": config["icon"]
            })

        return result

    def get_recommended_style(self, round: str) -> str:
        """根据面试轮次获取推荐的面试官风格"""
        # 推荐映射（基于之前的智能分配逻辑）
        recommendations = {
            "技术一面": "friendly",
            "技术二面": "professional",
            "技术三面": "challenging",
            "HR面": "friendly",
            "总监面": "challenging",
            "终面": "professional"
        }
        return recommendations.get(round, "friendly")

    def _get_system_prompt(self, position: str, round: str, interviewer_style: str = "friendly", resume: Optional[str] = None) -> str:
        """生成系统提示词"""
        style_config = self._get_interviewer_style(interviewer_style)

        base_prompt = f"""你是一位经验丰富的{position}面试官，正在进行{round}。

【面试官风格】
{style_config['personality']}

【重要交互要求】
1. 在候选人回答后，你必须先给出简短的互动反馈（如："{style_config['feedback_examples'][0]}"、"{style_config['feedback_examples'][1]}"等），让对话更自然流畅
2. 互动反馈要简短（1-5个字），不要过长，模拟真实面试的节奏
3. 反馈后再进行评分和提出下一个问题

【面试要求】
1. 提问要专业、有针对性，根据候选人的回答深入追问
2. 问题难度要循序渐进，从基础到进阶
3. 关注候选人的技术深度、项目经验、逻辑思维和沟通能力
4. 每次只问一个问题，等待候选人回答后再继续
5. 根据候选人的回答给出即时评分（0-10分）和改进提示

【面试流程】
- 开场：简单自我介绍和热身问题（1-2个）
- 基础知识：考察核心技术栈（2-3个）
- 深入探讨：项目经验和解决方案（2-3个）
- 场景问题：实际问题解决能力（1-2个）
- 收尾：候选人提问环节

总计8-10个问题，控制在15-20分钟内。"""

        if resume:
            base_prompt += f"\n\n【候选人简历】\n{resume}\n\n请根据简历内容针对性提问。"

        return base_prompt

    def _get_position_questions(self, position_id: str, round_name: str = None) -> tuple[str, List[Dict]]:
        """获取岗位相关问题提示和知识库参考题目

        Returns:
            (提示文本, 参考题目列表)
        """
        # 从岗位服务获取关键词
        keywords = position_service.get_position_keywords(position_id)
        position_info = position_service.get_position_by_id(position_id)

        if not position_info:
            return "", []

        # 构建问题提示
        keywords_str = "、".join(keywords) if keywords else "相关技能"
        full_name = position_service.get_position_full_name(position_id)

        # 从知识库获取参考题目（获取较多题目作为题库池）
        reference_questions = []
        try:
            reference_questions = knowledge_service.search_by_position(
                position=full_name,
                limit=50  # 获取50条作为参考池
            )
            print(f"[知识库] 为 {full_name} 获取了 {len(reference_questions)} 条参考题目")
        except Exception as e:
            print(f"[知识库] 获取参考题目失败: {e}")

        hint = f"重点考察：{keywords_str}（针对{full_name}岗位）"
        return hint, reference_questions

    def _generate_interview_plan(self, position: str, round: str, resume: Optional[str] = None, reference_questions: List[Dict] = None) -> dict:
        """生成动态面试计划

        Args:
            position: 岗位名称
            round: 面试轮次
            resume: 简历（可选）
            reference_questions: 知识库参考题目（可选）
        """
        # 构建知识库参考信息
        knowledge_context = ""
        if reference_questions:
            # 随机选择10条参考题目展示给LLM
            import random
            sample_questions = random.sample(reference_questions, min(10, len(reference_questions)))
            questions_preview = "\n".join([f"- {q.get('question', '')}" for q in sample_questions])
            knowledge_context = f"\n\n【知识库参考题目示例】（仅供参考，不要照搬，要结合候选人情况改编和延伸）：\n{questions_preview}"

        messages = [{
            "role": "user",
            "content": f"""作为{position}的{round}面试官，请为本次面试制定一个灵活的面试计划。

{"候选人简历：" + resume if resume else "无简历信息"}
{knowledge_context}

请设计面试主题和大致方向，但保持灵活性以便根据候选人表现调整。

【重要】如果有知识库参考题目，请理解其考察方向和知识点，但不要直接照搬，要：
1. 根据候选人简历个性化调整
2. 用自己的方式重新组织问题
3. 结合实际项目场景延伸

请按以下JSON格式输出面试计划：
{{
    "topics": ["开场热身", "基础技能", "项目经验", "深入技术", "场景问题"],
    "topic_descriptions": {{
        "开场热身": "简单介绍，缓解紧张",
        "基础技能": "考察核心技术栈基础知识",
        "项目经验": "了解实际项目经验和成果",
        "深入技术": "深入探讨技术细节和原理",
        "场景问题": "考察实际问题解决能力"
    }},
    "estimated_duration": "15-25分钟",
    "flexibility_note": "根据候选人回答质量动态调整深度和广度"
}}"""
        }]

        response_text = self._call_llm(messages, temperature=0.7)

        try:
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                plan = json.loads(json_match.group())
            else:
                plan = json.loads(response_text)

            # 添加运行时状态
            plan["current_topic_index"] = 0
            plan["completed_topics"] = []
            plan["should_continue"] = True

            return plan
        except Exception as e:
            print(f"[ERROR] 生成面试计划失败: {e}")
            # 返回默认计划
            return {
                "topics": ["开场热身", "核心技能", "项目经验", "综合评估"],
                "topic_descriptions": {
                    "开场热身": "简单介绍",
                    "核心技能": "技术基础",
                    "项目经验": "实践经验",
                    "综合评估": "综合能力"
                },
                "current_topic_index": 0,
                "completed_topics": [],
                "should_continue": True
            }

    def start_interview(self, request: InterviewStartRequest, db: Session) -> InterviewStartResponse:
        """开始面试"""
        # 生成会话ID
        session_id = f"session_{uuid.uuid4().hex[:16]}"

        # 获取面试官风格（优先使用用户选择，否则智能推荐）
        interviewer_style = request.interviewer_style
        if not interviewer_style:
            interviewer_style = self._auto_select_interviewer_style(request.round)
            print(f"[面试官分配] 用户未选择，自动推荐: {interviewer_style}")
        else:
            print(f"[面试官分配] 用户选择: {interviewer_style}")

        # 获取岗位完整名称
        position_full_name = position_service.get_position_full_name(request.position_id)

        # 获取知识库参考题目
        questions_guide, reference_questions = self._get_position_questions(request.position_id, request.round)

        # 生成面试计划（传入参考题目）
        interview_plan = self._generate_interview_plan(position_full_name, request.round, request.resume, reference_questions)
        print(f"[面试计划] {interview_plan}")

        # 生成系统提示词（使用面试官风格）
        system_prompt = self._get_system_prompt(position_full_name, request.round, interviewer_style, request.resume)

        # 获取当前主题
        current_topic = interview_plan["topics"][0] if interview_plan["topics"] else "开场"
        topic_desc = interview_plan.get("topic_descriptions", {}).get(current_topic, "")

        # 构建知识库参考（仅用于开场阶段，选择简单题目）
        knowledge_hint = ""
        if reference_questions:
            # 随机选择3条简单的参考题目
            import random
            sample = random.sample(reference_questions, min(3, len(reference_questions)))
            sample_text = "\n".join([f"- {q.get('question', '')}" for q in sample])
            knowledge_hint = f"\n\n【参考方向】（不要照搬，要自然改编）：\n{sample_text}"

        # 生成开场问题
        messages = [
            {
                "role": "user",
                "content": f"""现在开始{position_full_name}的{request.round}。

{questions_guide}

当前主题：{current_topic} - {topic_desc}
{knowledge_hint}

请提出第一个开场问题，要求：
1. 友好、专业的开场白
2. 一个简单的热身问题
3. 让候选人放松并进入状态
4. 如果有参考题目，理解其考察点，但要用自己的方式表达

直接输出问题，不要输出其他内容。"""
            }
        ]

        first_question = self._call_llm(messages, system=system_prompt, temperature=0.7)

        # 将参考题目保存到面试计划中
        interview_plan["reference_questions"] = reference_questions

        # 创建会话记录
        session = InterviewSession(
            session_id=session_id,
            user_id=request.user_id,
            position=position_full_name,  # 保存完整岗位名称
            round=request.round,
            resume=request.resume,
            interview_plan=interview_plan,  # 保存面试计划（包含参考题目）
            current_question=first_question,
            question_count=1,
            transcript=[
                {
                    "role": "interviewer",
                    "content": first_question,
                    "timestamp": datetime.utcnow().isoformat(),
                    "question_number": 1,
                    "style": interviewer_style,  # 保存面试官风格
                    "topic": current_topic  # 保存当前主题
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

        # 检查用户是否主动结束面试
        if request.finish_interview:
            print(f"[面试结束] 用户主动结束面试")
            session.is_finished = True
            session.finished_at = datetime.utcnow()
            db.commit()

            return AnswerResponse(
                next_question=None,
                instant_score=None,
                hint="感谢您参加本次面试，报告已生成",
                is_finished=True
            )

        # 构建对话历史
        messages = []
        for item in session.transcript[-6:]:  # 最近3轮对话
            role = "assistant" if item["role"] == "interviewer" else "user"
            messages.append({"role": role, "content": item["content"]})

        # 获取面试计划
        interview_plan = session.interview_plan or {}
        topics = interview_plan.get("topics", [])
        current_topic_index = interview_plan.get("current_topic_index", 0)
        completed_topics = interview_plan.get("completed_topics", [])

        # 判断是否完成所有主题
        all_topics_completed = current_topic_index >= len(topics)

        if not all_topics_completed:
            # 继续面试
            # 生成下一个问题（使用会话中保存的面试官风格，默认为 friendly）
            interviewer_style = session.transcript[0].get("style", "friendly") if session.transcript else "friendly"
            system_prompt = self._get_system_prompt(session.position, session.round, interviewer_style, session.resume)

            # 获取当前主题信息
            current_topic = topics[current_topic_index] if current_topic_index < len(topics) else "综合评估"
            topic_desc = interview_plan.get("topic_descriptions", {}).get(current_topic, "")

            # 动态知识库检索：根据候选人回答提取关键词并搜索相关题目
            dynamic_references = []
            try:
                # 简单关键词提取（从回答中提取技术词汇）
                answer_keywords = self._extract_tech_keywords(request.answer)
                if answer_keywords:
                    print(f"[知识库] 从回答中提取关键词: {answer_keywords}")
                    dynamic_references = knowledge_service.search_related_questions(
                        keywords=answer_keywords,
                        position=session.position,
                        limit=5
                    )
                    print(f"[知识库] 动态检索到 {len(dynamic_references)} 条相关题目")
            except Exception as e:
                print(f"[知识库] 动态检索失败: {e}")

            # 构建知识库参考提示
            knowledge_hint = ""
            if dynamic_references:
                # 使用动态检索结果
                ref_text = "\n".join([f"- {q.get('question', '')}" for q in dynamic_references[:3]])
                knowledge_hint = f"\n\n【相关参考题目】（可作为追问方向，但要自然延伸，不要照搬）：\n{ref_text}"
            else:
                # 使用初始参考题库
                reference_questions = interview_plan.get("reference_questions", [])
                if reference_questions:
                    import random
                    sample = random.sample(reference_questions, min(3, len(reference_questions)))
                    ref_text = "\n".join([f"- {q.get('question', '')}" for q in sample])
                    knowledge_hint = f"\n\n【参考题库】（可作为提问方向）：\n{ref_text}"

            messages.append({
                "role": "user",
                "content": f"""候选人已回答问题{session.question_count}。

【面试计划状态】
- 当前主题：{current_topic} - {topic_desc}
- 已完成主题：{', '.join(completed_topics) if completed_topics else '无'}
- 剩余主题：{', '.join(topics[current_topic_index+1:]) if current_topic_index+1 < len(topics) else '无'}
{knowledge_hint}

【重要】请严格按照你的面试官风格进行互动！

请执行以下任务：
1. 先给出简短的互动反馈（2-8个字，如："好的"、"明白了"、"不错"等），让对话更自然
2. 对候选人的回答进行评分（0-10分）
3. 给出改进提示（1-2句话，指出可以改进的地方）
4. **决定下一步动作**：
   - 如果候选人回答值得深入探讨，可以选择"延伸追问"（follow_up）
   - 如果候选人回答已经足够，选择"进入下一个问题"（next_topic）

【延伸追问的场景】（可选，不是必须）：
- 候选人提到了有趣的技术细节，值得深挖
- 回答不够具体，需要追问实现方式
- 发现了潜在的知识盲区，想要确认
- 候选人表现出色，想要挑战更高难度

【进入下一个问题的场景】：
- 当前主题已经考察充分
- 候选人回答清晰完整
- 需要推进面试进度

请按以下JSON格式输出：
{{
    "feedback": "好的",
    "score": 8.5,
    "hint": "回答不错，但可以更深入探讨具体的实现细节",
    "action": "follow_up",  // 或 "next_topic"
    "next_question": "问题内容",
    "topic_completed": false  // 当前主题是否已完成（如果action是next_topic，设为true）
}}"""
            })

            response_text = self._call_llm(messages, system=system_prompt, temperature=0.8)
            print(f"[DEBUG] Qwen 原始响应: {response_text}")

            # 解析响应
            try:
                # 尝试提取JSON
                import re
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    response_data = json.loads(json_match.group())
                else:
                    response_data = json.loads(response_text)

                print(f"[DEBUG] 解析后的数据: {response_data}")
                feedback = response_data.get("feedback", "好的")
                instant_score = response_data.get("score", 7.0)
                hint = response_data.get("hint", "")
                next_question = response_data.get("next_question", "")
                action = response_data.get("action", "next_topic")  # follow_up 或 next_topic
                topic_completed = response_data.get("topic_completed", False)

                print(f"[DEBUG] feedback={feedback}, score={instant_score}, action={action}, topic_completed={topic_completed}")
            except Exception as e:
                # 如果解析失败，使用默认值
                print(f"[DEBUG] JSON解析失败: {e}")
                feedback = "好的"
                instant_score = 7.0
                hint = ""
                next_question = response_text
                action = "next_topic"
                topic_completed = False

            # 更新最后一条候选人回答的评分和反馈
            session.transcript[-1]["score"] = instant_score
            session.transcript[-1]["hint"] = hint
            session.transcript[-1]["feedback"] = feedback

            # 更新面试计划状态
            if topic_completed and action == "next_topic":
                # 当前主题完成，移动到下一个主题
                if current_topic not in completed_topics:
                    completed_topics.append(current_topic)
                interview_plan["current_topic_index"] = current_topic_index + 1
                interview_plan["completed_topics"] = completed_topics

                # 获取新主题
                new_topic_index = interview_plan["current_topic_index"]
                if new_topic_index < len(topics):
                    new_topic = topics[new_topic_index]
                    print(f"[面试进度] 完成主题：{current_topic}，进入新主题：{new_topic}")
                else:
                    print(f"[面试进度] 所有主题已完成")
            else:
                # 延伸追问，保持当前主题
                print(f"[面试进度] 延伸追问，继续主题：{current_topic}")

            # 保存更新后的计划
            session.interview_plan = interview_plan
            flag_modified(session, "interview_plan")

            # 将反馈和问题组合（如果有反馈的话）
            if feedback:
                full_response = f"{feedback}\n\n{next_question}"
            else:
                full_response = next_question

            # 记录下一个问题
            session.question_count += 1
            session.current_question = full_response

            # 确定当前所在主题
            active_topic_index = interview_plan.get("current_topic_index", 0)
            active_topic = topics[active_topic_index] if active_topic_index < len(topics) else current_topic

            session.transcript.append({
                "role": "interviewer",
                "content": full_response,
                "timestamp": datetime.utcnow().isoformat(),
                "question_number": session.question_count,
                "feedback": feedback,  # 单独保存反馈用于统计
                "topic": active_topic,  # 保存当前主题
                "action": action  # 保存动作类型
            })
            flag_modified(session, "transcript")

            db.commit()

            return AnswerResponse(
                next_question=full_response,
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

        # 使用大模型分析面试表现
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

        response_text = self._call_llm(messages, system=system_prompt, temperature=0.5)

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
