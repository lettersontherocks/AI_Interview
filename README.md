# AI 面试练习平台

基于 Claude AI 的智能面试模拟系统，包含后端API服务和微信小程序前端。

## 项目结构

```
ai_interview/
├── api_service/              # Claude API 网关服务 (端口: 8002)
│   ├── main.py              # FastAPI 应用入口
│   ├── claude_service.py    # Claude API 调用封装
│   ├── config.py            # 配置管理
│   └── models.py            # 数据模型
│
├── apps/
│   ├── interview_backend/   # 面试业务后端 (端口: 8003)
│   │   ├── main.py         # FastAPI 应用入口
│   │   ├── config.py       # 业务配置
│   │   ├── api/            # API 路由
│   │   ├── services/       # 业务逻辑
│   │   ├── database/       # 数据库模型
│   │   └── models/         # 请求/响应模型
│   │
│   └── miniprogram/        # 微信小程序前端
│       ├── app.js          # 小程序入口
│       ├── app.json        # 全局配置
│       ├── pages/          # 页面目录
│       └── images/         # 图标资源
│
└── docs/
    └── API.md              # API 接口文档
```

## 功能特性

### 支持的岗位 (7个)
- 💻 前端工程师
- ⚙️ 后端工程师
- 📊 产品经理
- 🤖 算法工程师
- 📈 数据分析师
- 💼 销售
- 📢 市场运营

### 面试轮次 (4个)
- HR面 - 基本情况沟通
- 技术一面 - 基础技术考察
- 技术二面 - 深入技术探讨
- 总监面 - 综合能力评估

### 核心功能
- ✅ AI 智能面试官（8-10个渐进式问题）
- ✅ 即时评分反馈（0-10分 + 改进提示）
- ✅ 简历个性化提问
- ✅ 4维度综合评估报告
- ✅ VIP会员系统（免费1次/天，VIP无限）
- ✅ 面试历史记录

## 快速开始

### 前置要求

- Python 3.8+
- Claude API Key
- 微信开发者工具（开发小程序）

### 环境配置

1. **安装依赖**

```bash
# API 服务依赖
cd api_service
pip install -r requirements.txt

# 面试后端依赖
cd ../apps/interview_backend
pip install -r requirements.txt
```

2. **配置环境变量**

创建 `.env` 文件（或设置环境变量）：

```bash
# Claude API 配置
CLAUDE_API_KEY=your_claude_api_key_here

# 数据库（默认使用 SQLite）
DATABASE_URL=sqlite:///./ai_interview.db

# 微信小程序配置（可选）
WECHAT_APP_ID=your_app_id
WECHAT_APP_SECRET=your_app_secret
```

### 启动服务

#### 方式1: 分别启动（推荐开发）

```bash
# 终端1 - 启动 Claude API 网关
cd api_service
python main.py
# 运行在 http://localhost:8002

# 终端2 - 启动面试后端
cd apps/interview_backend
python main.py
# 运行在 http://localhost:8003
```

#### 方式2: 使用 Docker（推荐生产）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 测试后端

```bash
# 测试 API 网关
curl http://localhost:8002/health

# 测试面试后端
curl http://localhost:8003/

# 测试用户注册
curl -X POST "http://localhost:8003/api/v1/user/register?openid=test123&nickname=测试用户"
```

### 运行微信小程序

1. **打开微信开发者工具**
2. **导入项目**
   - 项目路径: `apps/miniprogram`
   - AppID: 选择"测试号"
3. **配置开发环境**
   - 详情 → 不校验合法域名（开发环境）
4. **编译运行**

详见 [apps/miniprogram/README.md](apps/miniprogram/README.md)

## API 文档

完整的 API 接口文档见 [docs/API.md](docs/API.md)

### 主要接口

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/v1/user/register` | POST | 用户注册 |
| `/api/v1/user/{user_id}` | GET | 获取用户信息 |
| `/api/v1/interview/start` | POST | 开始面试 |
| `/api/v1/interview/answer` | POST | 提交回答 |
| `/api/v1/interview/report/{session_id}` | GET | 获取面试报告 |

## 技术栈

### 后端
- **框架**: FastAPI
- **AI**: Claude API (Anthropic)
- **数据库**: SQLite (可切换 PostgreSQL/MySQL)
- **ORM**: SQLAlchemy
- **验证**: Pydantic

### 前端
- **平台**: 微信小程序
- **语言**: JavaScript (ES6+)
- **UI**: 原生组件 (WXML/WXSS)

## 数据库

项目使用 SQLite 作为默认数据库，数据文件：`ai_interview.db`

### 主要表结构

- **users** - 用户信息
- **interview_sessions** - 面试会话
- **interview_reports** - 面试报告
- **payments** - 支付记录

数据库会在首次启动时自动初始化。

## 部署

### 生产环境部署要点

1. **后端部署**
   - 使用 Gunicorn/Uvicorn 运行
   - 配置 Nginx 反向代理
   - 启用 HTTPS

2. **小程序部署**
   - 修改 `app.js` 中的 `baseUrl` 为生产地址
   - 在微信公众平台配置服务器域名
   - 提交审核并发布

3. **数据库**
   - 生产环境建议使用 PostgreSQL
   - 配置定期备份

详见各子项目的 README 文档。

## 开发说明

### 添加新的面试岗位

编辑 `apps/interview_backend/services/interview_service.py`:

```python
def _get_position_questions(self, position: str) -> str:
    questions_guide = {
        "新岗位名称": "重点考察：XXX、YYY、ZZZ",
        # ...
    }
```

同时更新小程序的 `pages/index/index.js` 中的岗位列表。

### 修改面试问题数量

在 `interview_service.py` 的 `process_answer` 方法中修改：

```python
should_continue = session.question_count < 10  # 修改此数字
```

## 许可证

本项目为演示项目，仅供学习参考使用。

## 相关文档

- [API 接口文档](docs/API.md)
- [小程序开发文档](apps/miniprogram/README.md)
