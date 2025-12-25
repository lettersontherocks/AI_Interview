# API 文档

## 基础信息

- **基础URL**: `http://localhost:8003/api/v1`
- **Content-Type**: `application/json`

## 端点列表

### 1. 用户管理

#### 1.1 用户注册

**POST** `/user/register`

注册新用户或获取已存在用户信息

**Query参数:**
- `openid` (string, required): 微信OpenID
- `nickname` (string, optional): 昵称
- `avatar` (string, optional): 头像URL

**响应示例:**
```json
{
  "user_id": "user_1a2b3c4d5e6f7g8h",
  "openid": "wx_openid_123",
  "nickname": "张三",
  "avatar": "https://example.com/avatar.jpg",
  "is_vip": false,
  "vip_expire_date": null,
  "free_count_today": 0,
  "created_at": "2024-01-01T00:00:00"
}
```

#### 1.2 获取用户信息

**GET** `/user/{user_id}`

**路径参数:**
- `user_id` (string, required): 用户ID

**响应示例:** (同上)

---

### 2. 面试流程

#### 2.1 开始面试

**POST** `/interview/start`

开始新的面试会话

**请求体:**
```json
{
  "position": "前端工程师",
  "round": "技术一面",
  "user_id": "user_1a2b3c4d5e6f7g8h",
  "resume": "3年前端开发经验，熟悉React、Vue等框架"
}
```

**字段说明:**
- `position` (enum): 岗位类型
  - `前端工程师`
  - `后端工程师`
  - `产品经理`
  - `算法工程师`
  - `数据分析师`
  - `销售`
  - `市场运营`
- `round` (enum): 面试轮次
  - `HR面`
  - `技术一面`
  - `技术二面`
  - `总监面`
- `user_id` (string): 用户ID
- `resume` (string, optional): 简历内容

**响应示例:**
```json
{
  "session_id": "session_1a2b3c4d5e6f",
  "question": "您好！欢迎参加面试。首先，请简单介绍一下自己的工作经历和技术栈？",
  "question_type": "开场"
}
```

**错误响应:**
- `404`: 用户不存在
- `403`: 今日免费次数已用完

#### 2.2 提交回答

**POST** `/interview/answer`

提交候选人的回答，获取下一个问题

**请求体:**
```json
{
  "session_id": "session_1a2b3c4d5e6f",
  "answer": "我叫张三，有3年前端开发经验..."
}
```

**响应示例 (继续面试):**
```json
{
  "next_question": "能详细说说React的核心思想吗？",
  "instant_score": 8.5,
  "hint": "回答很好，展现了扎实的基础",
  "is_finished": false
}
```

**响应示例 (面试结束):**
```json
{
  "next_question": null,
  "instant_score": null,
  "hint": "面试已结束，感谢您的参与！",
  "is_finished": true
}
```

**字段说明:**
- `next_question` (string | null): 下一个问题
- `instant_score` (float | null): 即时评分 (0-10)
- `hint` (string): 提示或反馈
- `is_finished` (boolean): 是否结束

#### 2.3 获取面试报告

**GET** `/interview/report/{session_id}`

获取完整的面试评估报告

**路径参数:**
- `session_id` (string): 会话ID

**响应示例:**
```json
{
  "session_id": "session_1a2b3c4d5e6f",
  "total_score": 85.5,
  "technical_skill": 88.0,
  "communication": 82.0,
  "logic_thinking": 86.0,
  "experience": 85.0,
  "suggestions": [
    "继续深入学习React底层原理，特别是Fiber架构",
    "提升系统设计能力，多了解大型项目架构",
    "加强算法和数据结构的训练"
  ],
  "transcript": [
    {
      "role": "interviewer",
      "content": "请介绍一下自己",
      "timestamp": "2024-01-01T10:00:00",
      "question_number": 1
    },
    {
      "role": "candidate",
      "content": "我叫张三...",
      "timestamp": "2024-01-01T10:01:00",
      "question_number": 1,
      "score": 8.5,
      "hint": "回答不错"
    }
  ],
  "created_at": "2024-01-01T10:15:00"
}
```

**字段说明:**
- `total_score` (float): 总分 (0-100)
- `technical_skill` (float): 技术能力评分
- `communication` (float): 表达能力评分
- `logic_thinking` (float): 逻辑思维评分
- `experience` (float): 项目经验评分
- `suggestions` (array): 改进建议列表
- `transcript` (array): 完整对话记录

---

## 完整流程示例

### Python

```python
import requests

BASE_URL = "http://localhost:8003/api/v1"

# 1. 注册用户
response = requests.post(
    f"{BASE_URL}/user/register",
    params={"openid": "wx_test_123", "nickname": "张三"}
)
user = response.json()
user_id = user["user_id"]

# 2. 开始面试
response = requests.post(
    f"{BASE_URL}/interview/start",
    json={
        "position": "前端工程师",
        "round": "技术一面",
        "user_id": user_id,
        "resume": "3年React经验"
    }
)
data = response.json()
session_id = data["session_id"]
print(f"问题1: {data['question']}")

# 3. 回答问题 (循环)
while True:
    answer = input("你的回答: ")

    response = requests.post(
        f"{BASE_URL}/interview/answer",
        json={"session_id": session_id, "answer": answer}
    )
    data = response.json()

    if data["instant_score"]:
        print(f"评分: {data['instant_score']}/10")
        print(f"提示: {data['hint']}")

    if data["is_finished"]:
        break

    print(f"下一个问题: {data['next_question']}")

# 4. 获取报告
response = requests.get(f"{BASE_URL}/interview/report/{session_id}")
report = response.json()
print(f"\n总分: {report['total_score']}")
print(f"技术能力: {report['technical_skill']}")
print(f"改进建议: {report['suggestions']}")
```

### JavaScript

```javascript
const BASE_URL = 'http://localhost:8003/api/v1';

// 1. 注册用户
const registerUser = async () => {
  const response = await fetch(
    `${BASE_URL}/user/register?openid=wx_test_123&nickname=张三`,
    { method: 'POST' }
  );
  return await response.json();
};

// 2. 开始面试
const startInterview = async (userId) => {
  const response = await fetch(`${BASE_URL}/interview/start`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      position: '前端工程师',
      round: '技术一面',
      user_id: userId,
      resume: '3年React经验'
    })
  });
  return await response.json();
};

// 3. 提交回答
const submitAnswer = async (sessionId, answer) => {
  const response = await fetch(`${BASE_URL}/interview/answer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      answer: answer
    })
  });
  return await response.json();
};

// 4. 获取报告
const getReport = async (sessionId) => {
  const response = await fetch(
    `${BASE_URL}/interview/report/${sessionId}`
  );
  return await response.json();
};

// 使用示例
(async () => {
  const user = await registerUser();
  const interview = await startInterview(user.user_id);
  console.log('第一个问题:', interview.question);

  // 提交回答...
  const result = await submitAnswer(interview.session_id, '我有3年经验...');
  console.log('评分:', result.instant_score);

  // 获取报告...
  const report = await getReport(interview.session_id);
  console.log('总分:', report.total_score);
})();
```

---

## 错误代码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 403 | 权限不足（如免费次数用完） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

**错误响应格式:**
```json
{
  "detail": "错误描述信息"
}
```

---

## 业务规则

### 免费配额
- 免费用户: 每天1次面试
- VIP会员: 无限次面试
- 单次购买: 购买后立即可用

### 面试流程
- 每次面试 8-10 个问题
- 问题类型: 开场 → 基础 → 深入 → 场景 → 收尾
- 时长: 约 15-20 分钟
- 评分范围: 0-100 分

### 数据保留
- 面试记录永久保存
- 报告可重复获取
- 对话历史完整记录

---

## 互动式文档

启动服务后，访问以下地址查看交互式API文档:

- **Swagger UI**: http://localhost:8003/docs
- **ReDoc**: http://localhost:8003/redoc

在Swagger UI中可以直接测试所有API端点！
