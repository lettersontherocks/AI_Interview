# 🔐 安全配置指南

本文档介绍如何正确配置AI面试系统的敏感信息，避免密钥泄露。

## ⚠️ 安全警告

**永远不要将以下内容提交到Git仓库：**
- `.env` 文件
- API密钥和Token
- 数据库密码
- 任何其他敏感信息

## 📋 快速开始

### 1. 创建 `.env` 文件

```bash
# 复制示例文件
cd /path/to/ai_interview
cp .env.example .env
```

### 2. 填写必需配置

编辑 `.env` 文件，至少填写以下**必需**字段：

```bash
# 数据库密码（必需）
POSTGRES_PASSWORD=你的安全密码

# 阿里云DashScope API Key（必需）
DASHSCOPE_API_KEY=sk-your-api-key-here
```

### 3. 填写可选配置

根据需要填写以下可选字段：

```bash
# 火山引擎TTS（如果使用语音功能）
VOLCENGINE_APP_ID=你的AppID
VOLCENGINE_ACCESS_TOKEN=你的AccessToken

# 微信小程序（如果使用微信登录）
WECHAT_APP_ID=你的小程序AppID
WECHAT_APP_SECRET=你的小程序AppSecret

# Elasticsearch（如果有认证）
ES_USERNAME=你的ES用户名
ES_PASSWORD=你的ES密码
```

### 4. 启动服务

```bash
# 使用Docker Compose启动
docker-compose up -d

# 查看日志
docker-compose logs -f interview-backend
```

## 🔑 如何获取各项密钥

### 阿里云DashScope API Key

1. 访问 [阿里云DashScope控制台](https://dashscope.console.aliyun.com/)
2. 登录你的阿里云账号
3. 进入"API-KEY管理"页面
4. 创建新的API Key
5. 复制Key到 `.env` 文件的 `DASHSCOPE_API_KEY`

### 火山引擎豆包TTS

1. 访问 [火山引擎控制台](https://console.volcengine.com/)
2. 开通"语音合成"服务
3. 获取 AppID 和 Access Token
4. 填写到 `.env` 文件

### 微信小程序

1. 登录 [微信公众平台](https://mp.weixin.qq.com/)
2. 进入你的小程序管理后台
3. 在"开发" → "开发管理" → "开发设置"中找到：
   - AppID (小程序ID)
   - AppSecret (小程序密钥)
4. 填写到 `.env` 文件

## 🔒 安全最佳实践

### 1. 密码强度要求

数据库密码应满足：
- 至少12位字符
- 包含大小写字母、数字和特殊字符
- 不使用常见单词或个人信息

```bash
# ❌ 弱密码
POSTGRES_PASSWORD=123456

# ✅ 强密码
POSTGRES_PASSWORD=Xy9$mK2!pL4@nR8w
```

### 2. 环境隔离

不同环境使用不同的配置：

```bash
# 开发环境
.env.development

# 生产环境
.env.production

# 测试环境
.env.test
```

在 `docker-compose.yml` 中指定：

```yaml
env_file:
  - .env.production  # 使用生产环境配置
```

### 3. 定期更换密钥

建议每3-6个月更换一次：
- 数据库密码
- API密钥
- Access Token

### 4. 最小权限原则

- 数据库用户只授予必需的权限
- API密钥使用专用账号，避免使用主账号
- 定期审计访问日志

## 🚨 安全检查清单

部署前请确认：

- [ ] `.env` 文件已创建并填写所有必需字段
- [ ] `.env` 文件已加入 `.gitignore`
- [ ] 数据库密码足够强（至少12位）
- [ ] API密钥有效且未过期
- [ ] HTTPS已配置（生产环境必需）
- [ ] CORS已限制为具体域名（`ALLOWED_ORIGINS`）
- [ ] 防火墙规则已配置
- [ ] 日志监控已启用

## 🔧 验证配置

启动应用后，检查配置是否正确：

```bash
# 查看启动日志
docker-compose logs interview-backend

# 应该看到类似输出：
# ✅ 配置验证通过
# 📊 运行环境: production
# 🌐 数据库: postgres:5432/ai_interview
```

如果看到错误：

```bash
# ❌ 缺少必需的环境变量配置！
# 缺少的配置项：
#   - 阿里云DashScope API Key (dashscope_api_key)
```

说明 `.env` 文件配置不完整，请补充缺失的字段。

## 📞 遇到问题？

1. **配置验证失败**：检查 `.env` 文件是否存在且格式正确
2. **API调用失败**：验证API Key是否有效
3. **数据库连接失败**：检查密码是否正确，数据库是否启动

## 🔄 更新配置

修改 `.env` 文件后，需要重启服务：

```bash
# 重启服务
docker-compose restart interview-backend

# 或重新构建（如果修改了Dockerfile）
docker-compose up -d --build
```

## 📚 相关文档

- [Docker Compose文档](https://docs.docker.com/compose/)
- [阿里云DashScope文档](https://help.aliyun.com/zh/dashscope/)
- [火山引擎TTS文档](https://www.volcengine.com/docs/6561/79823)
- [微信小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
