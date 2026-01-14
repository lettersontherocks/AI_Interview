# 日志系统迁移指南

## 📋 概述

本指南说明如何将现有的 `print()` 语句替换为结构化日志系统。

---

## 🎯 替换规则

### 1. 导入日志模块

在每个文件顶部添加：

```python
import logging

logger = logging.getLogger(__name__)
```

### 2. 替换 print() 语句

| 原有代码 | 替换为 | 日志级别 |
|---------|--------|---------|
| `print("调试信息")` | `logger.debug("调试信息")` | DEBUG |
| `print("✅ 成功消息")` | `logger.info("✅ 成功消息")` | INFO |
| `print("[DEBUG] xxx")` | `logger.debug("xxx")` | DEBUG |
| `print("[ERROR] xxx")` | `logger.error("xxx")` | ERROR |
| `print("警告: xxx")` | `logger.warning("警告: xxx")` | WARNING |
| `print(f"用户{user_id}...")` | `logger.info(f"用户{user_id}...")` | INFO |

### 3. 异常日志

```python
# ❌ 旧方式
try:
    ...
except Exception as e:
    print(f"错误: {str(e)}")
    import traceback
    traceback.print_exc()

# ✅ 新方式
try:
    ...
except Exception as e:
    logger.error(f"错误: {str(e)}", exc_info=True)  # 自动记录堆栈
```

### 4. 添加上下文信息

```python
# ✅ 推荐：使用 extra 参数添加结构化数据
logger.info(
    "用户开始面试",
    extra={
        "user_id": user_id,
        "session_id": session_id,
        "position": position_name
    }
)
```

---

## 📝 具体文件修改示例

### services/interview_service.py

#### 原代码：
```python
print(f"[面试服务] 开始面试 - 用户: {user_id}, 岗位: {position}")
```

#### 修改后：
```python
logger.info(
    "开始面试",
    extra={
        "user_id": user_id,
        "position": position,
        "round": round
    }
)
```

---

### api/routes.py

#### 原代码：
```python
print(f"[DEBUG] 收到开始面试请求: position_id={request.position_id}")
```

#### 修改后：
```python
logger.debug(
    "收到开始面试请求",
    extra={
        "position_id": request.position_id,
        "round": request.round,
        "user_id": request.user_id
    }
)
```

---

### services/qwen_service.py

#### 原代码：
```python
print(f"调用 Qwen API 出错: {str(e)}")
raise Exception(f"调用 Qwen API 失败: {str(e)}")
```

#### 修改后：
```python
logger.error(f"调用 Qwen API 失败: {str(e)}", exc_info=True)
raise Exception(f"调用 Qwen API 失败: {str(e)}")
```

---

## 🔧 批量替换脚本

创建一个简单的 Python 脚本进行批量替换（仅供参考）：

```python
#!/usr/bin/env python3
"""
批量替换 print() 为 logger
注意：这只是简单替换，复杂情况需要手动调整
"""
import re
import os

def replace_prints_in_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 在文件开头添加 logger 导入（如果没有）
    if 'logging.getLogger' not in content:
        import_pos = content.find('import ')
        if import_pos != -1:
            end_of_imports = content.find('\n\n', import_pos)
            content = (content[:end_of_imports] +
                      '\nimport logging\n\nlogger = logging.getLogger(__name__)\n' +
                      content[end_of_imports:])

    # 替换 print 语句
    replacements = [
        (r'print\(f?"?\[DEBUG\]([^"]+)"?\)', r'logger.debug(\1)'),
        (r'print\(f?"?\[ERROR\]([^"]+)"?\)', r'logger.error(\1)'),
        (r'print\(f?"?❌([^"]+)"?\)', r'logger.error("❌\1")'),
        (r'print\(f?"?✅([^"]+)"?\)', r'logger.info("✅\1")'),
        (r'print\(f?"?⚠️([^"]+)"?\)', r'logger.warning("⚠️\1")'),
        (r'print\(f?"([^"]+)"\)', r'logger.info(f"\1")'),
        (r'print\("([^"]+)"\)', r'logger.info("\1")'),
    ]

    for pattern, repl in replacements:
        content = re.sub(pattern, repl, content)

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    return False

# 使用示例
if __name__ == "__main__":
    files_to_process = [
        "services/interview_service.py",
        "services/qwen_service.py",
        "api/routes.py",
        # 添加更多文件...
    ]

    for file in files_to_process:
        if replace_prints_in_file(file):
            print(f"✅ 已处理: {file}")
        else:
            print(f"⏭️  跳过: {file}")
```

---

## 📊 日志级别使用指南

| 级别 | 何时使用 | 示例 |
|------|----------|------|
| **DEBUG** | 调试信息，开发时使用 | 函数参数、中间变量值 |
| **INFO** | 正常的业务流程 | 用户登录、面试开始、API调用 |
| **WARNING** | 可能的问题，但不影响运行 | 配额即将用完、慢请求 |
| **ERROR** | 错误，需要关注 | API调用失败、数据库错误 |
| **CRITICAL** | 严重错误，服务可能中断 | 数据库连接失败 |

---

## ✅ 验证日志系统

### 1. 启动应用后检查：

```bash
# 查看日志文件是否生成
ls -lh logs/

# 实时查看日志
tail -f logs/app.log

# 查看错误日志
tail -f logs/error.log
```

### 2. 发送测试请求：

```bash
# 测试请求
curl http://localhost:8003/health

# 检查日志中是否有请求记录
grep "Request" logs/app.log
```

### 3. 检查日志格式：

```bash
# 查看最新10条日志
tail -10 logs/app.log
```

预期输出：
```
2024-01-14 10:30:45 [INFO] [ai_interview] 🚀 应用启动中...
2024-01-14 10:30:45 [INFO] [ai_interview] 📊 环境: development
2024-01-14 10:30:46 [INFO] [ai_interview] ✅ 数据库初始化完成
2024-01-14 10:31:10 [INFO] [ai_interview] 📥 Request started: GET /health
2024-01-14 10:31:10 [INFO] [ai_interview] ✅ Request completed: GET /health - 200 (5.23ms)
```

---

## 🔍 日志查询示例

```bash
# 查找特定用户的所有日志
grep "user_abc123" logs/app.log

# 查找所有错误
grep "ERROR" logs/app.log

# 查找特定时间段的日志
grep "2024-01-14 10:" logs/app.log

# 查找慢请求（超过2秒）
grep "Slow request" logs/app.log

# 统计今天的错误数量
grep "ERROR" logs/app.log | grep "$(date '+%Y-%m-%d')" | wc -l
```

---

## 📦 部署注意事项

### 生产环境建议：

1. **启用 JSON 格式日志**：
```python
# config.py
log_json_format: bool = True  # 生产环境改为 True
```

2. **调整日志级别**：
```python
# .env
LOG_LEVEL=INFO  # 生产环境不使用 DEBUG
```

3. **配置日志轮转**：
   - 已内置按天轮转（保留30天）
   - 错误日志按大小轮转（100MB）

4. **定期清理**：
```bash
# 添加到 crontab
0 2 * * * /path/to/scripts/clean_logs.sh 30
```

---

## 🎓 最佳实践

1. **不要在循环中打大量日志**
2. **敏感信息（密码、token）不要记录**
3. **使用 extra 参数添加结构化信息**
4. **ERROR 级别一定要包含完整堆栈（exc_info=True）**
5. **生产环境不要使用 DEBUG 级别**

---

## 🚀 后续优化方向

1. **集成 Sentry 进行错误追踪**
2. **配置日志告警（钉钉/邮件）**
3. **集成 ELK/Grafana Loki 进行日志分析**
4. **添加性能指标监控**
5. **配置日志采样（高流量场景）**

---

**祝您日志系统升级顺利！** 🎉
