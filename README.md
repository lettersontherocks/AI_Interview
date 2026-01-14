# AI 面试练习平台

基于 Claude API 的智能面试模拟系统，支持微信小程序和 iOS 双端应用。

## 项目简介

AI 面试练习平台是一个完整的面试模拟系统，通过 Claude 3.5 Sonnet 提供真实的 AI 面试官体验。系统包含后端 API 服务、微信小程序和 iOS 原生应用，为求职者提供专业的面试练习环境。

### 核心价值

- **真实面试体验**：AI 面试官基于岗位和轮次提出专业问题，支持多轮对话
- **即时反馈**：每个回答获得评分和改进建议，帮助快速提升
- **专业报告**：五维度能力评估，直观展示优势与不足
- **灵活交互**：支持文字和语音输入，提供聊天和沉浸两种模式

---

## 功能特性

### 1. 智能面试系统

**多岗位覆盖**
- 技术类：前端、后端、算法、移动端、全栈、DevOps、测试、架构师等
- 产品类：产品经理、产品运营、数据产品等
- 业务类：销售、市场、运营、客服等
- 支持 20+ 个不同岗位

**面试轮次选择**
- HR 面：基本情况、稳定性、职业规划
- 技术一面/二面/三面：技术深度递进
- 总监面：综合能力、团队协作
- 终面：战略思维、价值观

**个性化提问**
- 可上传简历，AI 根据简历内容定制问题
- 根据回答质量动态调整问题难度
- 8-10 个渐进式问题，模拟真实面试节奏

**面试官风格**
- 严格型：高标准要求，注重细节
- 友好型：轻松氛围，鼓励发挥
- 思考引导型：引导深入思考，挖掘潜力

### 2. 实时交互体验

**双模式输入**
- 文字输入：打字回答，适合详细表达
- 语音输入：语音转文字（集成百度 ASR），模拟真实对话

**即时评分系统**
- 每个回答获得 0-10 分评分
- 即时改进提示，指出回答不足
- 帮助快速调整答题策略

**沉浸式界面**
- 聊天模式：传统对话界面，便于查看历史
- 沉浸模式：专注面试，AI 语音播报问题（火山引擎 TTS）
- 一键切换，适应不同使用场景

### 3. 专业面试报告

**五维度评估**
```
技术能力 (Technical Skill)      - 专业知识、技术深度
沟通表达 (Communication)         - 表达能力、逻辑清晰
逻辑思维 (Logic Thinking)        - 分析能力、结构化思维
问题解决 (Problem Solving)       - 解决方案、应变能力
项目经验 (Project Experience)    - 实践经验、成果展示
```

**可视化展示**
- 雷达图：直观展示五个维度的能力分布
- 总分评级：优秀、良好、中等、及格、待提升
- 详细建议：针对每个维度的改进方案

**对话回放**
- 完整的面试对话记录
- 每个问答的评分和反馈
- 支持导出和分享

### 4. VIP 会员系统

**配额管理**
- 免费用户：每天 1 次免费面试
- 普通 VIP：每天 10 次面试
- 超级 VIP：无限次面试

**会员功能**
- 自动配额刷新（UTC 时区）
- 会员到期自动降级
- 微信支付集成（小程序）

### 5. 用户管理

**账户功能**
- 微信一键登录（小程序）
- 面试历史记录
- 继续未完成的面试
- 个人信息管理

**数据管理**
- 本地缓存清理
- 音频文件自动清理（三层机制）
- 隐私保护

---

## 技术架构

### 项目结构

```
ai_interview/
├── apps/
│   ├── interview_backend/      # FastAPI 后端服务
│   │   ├── api/               # API 路由
│   │   │   ├── interview.py  # 面试接口
│   │   │   ├── user.py        # 用户管理
│   │   │   ├── payment.py     # 支付功能
│   │   │   └── position.py    # 岗位数据
│   │   ├── services/          # 业务逻辑
│   │   │   ├── interview_service.py  # 面试核心逻辑
│   │   │   ├── claude_service.py     # Claude API 封装
│   │   │   ├── tts_service.py        # 语音合成
│   │   │   └── asr_service.py        # 语音识别
│   │   ├── database/          # 数据库层
│   │   │   ├── models.py     # SQLAlchemy 模型
│   │   │   └── database.py   # 数据库连接
│   │   └── models/            # Pydantic 数据模型
│   │
│   ├── miniprogram/           # 微信小程序
│   │   ├── pages/
│   │   │   ├── index/        # 首页 - 选择岗位/轮次/风格
│   │   │   ├── prepare/      # 准备页 - 加载动画
│   │   │   ├── interview/    # 面试页 - 双模式界面
│   │   │   ├── report/       # 报告页 - 五维度评估
│   │   │   ├── history/      # 历史记录
│   │   │   ├── profile/      # 个人中心
│   │   │   └── vip/          # VIP 会员
│   │   ├── app.js            # 全局逻辑（登录、配额检查）
│   │   └── config.js         # 环境配置
│   │
│   └── iosAPP/               # iOS 应用 (SwiftUI)
│       ├── ViewModels/       # MVVM 架构 - 视图模型
│       ├── Views/            # 界面层
│       ├── Models/           # 数据模型
│       ├── Services/         # 网络服务
│       └── Utils/            # 工具类
│
├── migrations/               # 数据库迁移
├── static/                  # 静态文件（TTS 音频）
└── docker-compose.yml       # Docker 编排
```

### 技术栈

**后端**
- Python 3.9+ / FastAPI
- PostgreSQL 14+
- SQLAlchemy 2.0+ ORM
- Claude API 3.5 Sonnet
- 火山引擎 TTS（语音合成）
- 百度 ASR（语音识别）

**微信小程序**
- JavaScript ES6+
- WXML/WXSS
- 微信 API（登录、支付、录音）

**iOS 应用**
- Swift 5.0+ / SwiftUI
- Combine（响应式编程）
- iOS 16.0+ 部署目标
- XcodeGen 项目管理

---

## 快速开始

### 环境要求

- Python 3.9+
- PostgreSQL 14+
- Claude API Key
- 微信开发者工具（开发小程序）
- Xcode 14+（开发 iOS）

### 1. 配置环境变量

创建 `apps/interview_backend/.env`：

```bash
# Claude API
ANTHROPIC_API_KEY=sk-ant-xxx

# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/ai_interview

# 微信小程序
WECHAT_APP_ID=wxXXXXXXXX
WECHAT_APP_SECRET=your_secret
WECHAT_MCH_ID=your_mch_id
WECHAT_API_KEY=your_api_key

# 火山引擎 TTS
VOLCENGINE_APP_ID=your_app_id
VOLCENGINE_TOKEN=your_token

# 百度 ASR
BAIDU_APP_ID=your_app_id
BAIDU_API_KEY=your_api_key
BAIDU_SECRET_KEY=your_secret_key
```

### 2. 初始化数据库

```bash
createdb ai_interview
cd apps/interview_backend
psql -U postgres -d ai_interview < ../../migrations/add_vip_type_column.sql
```

### 3. 启动后端

```bash
cd apps/interview_backend
pip install -r requirements.txt
python main.py
```

访问 http://localhost:8000/docs 查看 API 文档

### 4. 启动微信小程序

1. 打开微信开发者工具
2. 导入项目：`apps/miniprogram`
3. 修改 `config.js` 配置后端地址
4. 编译运行

### 5. 启动 iOS 应用

```bash
cd apps/iosAPP
xcodegen generate
open AIInterviewApp.xcodeproj
```

---

## 核心功能演示

### 面试流程

```
1. 选择岗位、轮次、面试官风格
   └─> 可选上传简历

2. AI 生成第一个问题
   └─> 支持语音播报（TTS）

3. 用户回答
   ├─> 文字输入：打字回答
   └─> 语音输入：录音转文字（ASR）

4. AI 实时评分
   ├─> 0-10 分评分
   └─> 改进建议

5. 继续下一题（共 8-10 题）
   └─> 难度动态调整

6. 生成面试报告
   ├─> 五维度评估
   ├─> 雷达图可视化
   └─> 详细改进建议
```

### API 接口示例

**开始面试**
```http
POST /api/v1/interview/start
{
  "position_id": "frontend",
  "position_name": "前端工程师",
  "round": "技术一面",
  "user_id": "user_123",
  "resume": "简历内容（可选）",
  "interviewer_style": "friendly"
}

Response:
{
  "session_id": "session_xxx",
  "question": "请介绍一下你最近的前端项目经验",
  "audio_url": "/static/tts/xxx.mp3"
}
```

**提交回答**
```http
POST /api/v1/interview/answer
{
  "session_id": "session_xxx",
  "user_id": "user_123",
  "answer": "我最近开发了一个..."
}

Response:
{
  "next_question": "你在项目中遇到的最大挑战是什么？",
  "instant_score": 8.5,
  "hint": "回答很好，建议补充更多技术细节",
  "is_finished": false,
  "audio_url": "/static/tts/yyy.mp3"
}
```

**获取报告**
```http
GET /api/v1/interview/report/{session_id}

Response:
{
  "total_score": 85.5,
  "technical_skill": 88.0,
  "communication": 82.0,
  "logic_thinking": 86.0,
  "problem_solving": 84.0,
  "project_experience": 87.0,
  "suggestions": [
    "加强对底层原理的理解",
    "提升问题定位和解决能力"
  ],
  "transcript": [...]
}
```

---

## 数据库设计

### 核心表结构

**users** - 用户表
```sql
user_id         VARCHAR(50) PRIMARY KEY
openid          VARCHAR(100)  -- 微信 openid
nickname        VARCHAR(100)
avatar          TEXT
vip_type        VARCHAR(20)   -- null/normal/super
daily_limit     INTEGER       -- 每日配额
vip_expire_date TIMESTAMP     -- VIP 到期时间
free_count_today INTEGER      -- 今日已用次数
created_at      TIMESTAMP
```

**interview_sessions** - 面试会话
```sql
session_id      VARCHAR(50) PRIMARY KEY
user_id         VARCHAR(50)
position        VARCHAR(100)
round           VARCHAR(50)
question_count  INTEGER
is_finished     BOOLEAN
context         TEXT          -- 对话上下文（JSON）
created_at      TIMESTAMP
```

**interview_reports** - 面试报告
```sql
report_id           VARCHAR(50) PRIMARY KEY
session_id          VARCHAR(50)
total_score         FLOAT
technical_skill     FLOAT
communication       FLOAT
logic_thinking      FLOAT
problem_solving     FLOAT
project_experience  FLOAT
suggestions         TEXT      -- 改进建议（JSON）
transcript          TEXT      -- 对话记录（JSON）
created_at          TIMESTAMP
```

---

## 部署说明

### Docker 部署

```bash
docker-compose up -d
```

### 生产环境配置

**后端**
- 使用 Gunicorn/Uvicorn 运行
- Nginx 反向代理
- HTTPS 证书配置

**微信小程序**
- 修改生产 API 地址
- 微信公众平台配置服务器域名
- 提交审核发布

**iOS 应用**
- 配置生产环境 URL
- Apple Developer 证书配置
- App Store Connect 上传

---

## 常见问题

**Q: Claude API 调用失败？**
A: 检查 API Key 配置、网络连接和 API 配额

**Q: 微信小程序登录失败？**
A: 确认 AppID/AppSecret 配置正确，服务器域名已配置

**Q: TTS 语音合成不工作？**
A: 检查火山引擎 API 配置和 `static/tts/` 目录权限

**Q: 数据库连接失败？**
A: 确认 PostgreSQL 运行正常，连接字符串格式正确

---

## 项目特色

1. **完整的产品闭环**：从面试准备到报告生成，完整的用户体验
2. **多端支持**：微信小程序 + iOS 原生应用，覆盖主流平台
3. **AI 驱动**：基于 Claude 3.5 Sonnet，提供真实的面试体验
4. **商业化就绪**：VIP 系统、支付集成，可直接上线运营
5. **可扩展性**：模块化设计，易于添加新岗位和功能

---

## 许可证

MIT License

---

**最后更新**: 2026-01-14
