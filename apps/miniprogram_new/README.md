# AI 面试小程序

微信小程序前端，配合后端API提供智能面试练习功能。

## 功能

- 7个岗位 × 4个面试轮次
- 实时AI对话（8-10题）
- 即时评分和反馈
- 4维度综合评估报告
- VIP会员系统
- 面试历史记录

## 项目结构

```
miniprogram/
├── app.js, app.json, app.wxss    # 全局配置
├── sitemap.json                  # 搜索配置
├── project.config.json           # 开发工具配置
├── pages/                        # 页面
│   ├── index/                    # 首页 - 岗位选择
│   ├── interview/                # 面试页 - 对话界面
│   ├── report/                   # 报告页 - 评估结果
│   └── profile/                  # 个人中心
├── images/                       # TabBar图标
│   ├── home.png
│   ├── home-active.png
│   ├── profile.png
│   └── profile-active.png
└── create_icons.py               # 图标生成脚本
```

## 快速开始

### 1. 准备TabBar图标

```bash
# 使用Python生成占位图标
python3 create_icons.py
```

或从 [IconFont](https://www.iconfont.cn/) 下载专业图标（81x81px）。

### 2. 配置后端地址

编辑 `app.js`:

```javascript
globalData: {
  baseUrl: 'http://localhost:8003/api/v1'  // 开发环境
  // baseUrl: 'https://your-domain.com/api/v1'  // 生产环境
}
```

### 3. 打开微信开发者工具

1. 导入项目（选择 `miniprogram` 目录）
2. AppID: 选择"测试号"
3. 详情 → 不校验合法域名（开发环境）
4. 点击"编译"

## API对接

小程序调用的后端接口：

| 接口 | 说明 |
|------|------|
| `POST /user/register` | 用户注册 |
| `GET /user/{user_id}` | 获取用户信息 |
| `POST /interview/start` | 开始面试 |
| `POST /interview/answer` | 提交回答 |
| `GET /interview/report/{id}` | 获取报告 |

详见 [../../docs/API.md](../../docs/API.md)

## 部署

### 开发环境
- 使用本地API（localhost:8003）
- 微信工具关闭URL校验

### 生产环境
1. 修改 `app.js` 中的 `baseUrl` 为HTTPS地址
2. 微信公众平台配置服务器域名
3. 上传代码并提交审核

## 技术栈

- 微信小程序原生框架
- JavaScript (ES6+)
- WXML/WXSS
