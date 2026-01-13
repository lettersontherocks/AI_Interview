# ⚡ 缓存优化文档

本文档介绍 AI 面试系统的缓存实现和使用方法。

## 📋 缓存概览

系统使用 Python 内置的 `functools.lru_cache` 实现轻量级缓存，无需额外依赖（如 Redis），降低运维复杂度。

### 已实现的缓存

| 缓存项 | 类型 | 大小 | TTL | 说明 |
|--------|------|------|-----|------|
| 知识库岗位查询 | LRU | 128 | 永久* | 缓存 ES 查询结果，减少网络 I/O |
| 面试官风格配置 | 静态 | 8 | 永久 | 固定配置数据，应用启动时加载 |
| 岗位配置数据 | 类变量 | - | 永久 | positions.json 仅加载一次 |

\* 可通过 API 手动清除

---

## 🎯 缓存实现细节

### 1. 知识库岗位查询缓存

**位置**: `services/knowledge_service.py:203-253`

**实现**:
```python
@lru_cache(maxsize=128)
def _cached_search_by_position(self, position: str, limit: int) -> tuple:
    """缓存 ES 查询结果"""
    results = self.search_questions(
        query=position,
        position=position,
        size=limit,
        search_type="hybrid"
    )
    return tuple(results)  # 转为 tuple 以支持缓存
```

**效果**:
- ✅ 同一岗位的查询直接从内存返回，避免重复调用 Elasticsearch
- ✅ 减少网络延迟（ES 查询从 100-500ms 降至 <1ms）
- ✅ 降低 ES 服务器负载
- ⚠️ 注意：缓存的是 **ES 原始结果**，`random.sample` 仍在使用时执行

**缓存键**: `(position, limit)` - 例如 `("Python后端开发 - Django开发", 50)`

**命中率监控**:
```bash
# 查看缓存统计
GET /admin/cache-stats

# 响应示例
{
  "knowledge_service": {
    "position_cache": {
      "hits": 45,
      "misses": 8,
      "maxsize": 128,
      "currsize": 8,
      "hit_rate": "84.91%"
    },
    "total_queries": 53,
    "last_cache_clear": "2025-01-13T10:30:00"
  }
}
```

---

### 2. 面试官风格配置缓存

**位置**: `services/interview_service.py:88-122`

**实现**:
```python
@staticmethod
@lru_cache(maxsize=8)
def _get_interviewer_style(style: str = "friendly") -> dict:
    """静态缓存：面试官风格固定配置"""
    styles = {
        "friendly": {...},
        "professional": {...},
        ...
    }
    return styles.get(style, styles["friendly"])
```

**效果**:
- ✅ 避免每次调用都重新构建 styles 字典（虽然开销很小，但调用频繁）
- ✅ maxsize=8 足够缓存所有 4 种风格
- ✅ 使用 `@staticmethod` 避免 self 参数影响缓存键

**缓存键**: `(style,)` - 例如 `("friendly",)`, `("professional",)`

---

### 3. 岗位配置数据缓存

**位置**: `services/position_service.py:8-42`

**实现**:
```python
class PositionService:
    # 类级别缓存（所有实例共享）
    _config_cache = None
    _position_map_cache = None

    def __init__(self):
        if PositionService._config_cache is None:
            # 首次加载 positions.json
            with open(config_path, 'r', encoding='utf-8') as f:
                PositionService._config_cache = json.load(f)

        # 使用缓存
        self.config = PositionService._config_cache
        self.position_map = PositionService._position_map_cache
```

**效果**:
- ✅ positions.json 仅在应用启动时加载一次
- ✅ 避免重复磁盘 I/O
- ✅ 多个实例共享同一份数据

**日志输出**:
```
[岗位配置] 首次加载 positions.json
[岗位配置] 已加载 4 个分类
[岗位配置] 映射表构建完成，共 27 个岗位
```

---

## 🔧 缓存管理

### 查看缓存统计

```bash
GET http://localhost:8003/admin/cache-stats
```

**响应示例**:
```json
{
  "knowledge_service": {
    "position_cache": {
      "hits": 120,
      "misses": 15,
      "maxsize": 128,
      "currsize": 12,
      "hit_rate": "88.89%"
    },
    "total_queries": 135,
    "last_cache_clear": "2025-01-13T08:00:00"
  },
  "timestamp": "2025-01-13T12:34:56"
}
```

**字段说明**:
- `hits`: 缓存命中次数
- `misses`: 缓存未命中次数（需查询 ES）
- `currsize`: 当前缓存条目数
- `hit_rate`: 缓存命中率（越高越好）

---

### 清除缓存

**使用场景**:
- 题库更新后需要刷新缓存
- 岗位配置修改后需要重新加载
- 测试缓存功能

**API 调用**:
```bash
POST http://localhost:8003/admin/clear-cache
```

**响应**:
```json
{
  "status": "success",
  "message": "缓存已清空",
  "timestamp": "2025-01-13T12:45:00"
}
```

**注意**:
- 仅清除知识库缓存
- 岗位配置缓存需要重启应用才能清除（或调用 `PositionService.clear_cache()`）

---

## 📊 性能提升

### 优化前 vs 优化后

| 操作 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 岗位题库查询（首次） | 150-300ms | 150-300ms | - |
| 岗位题库查询（缓存命中） | 150-300ms | <1ms | **99%+** |
| 面试官风格获取 | 0.01ms | 0.001ms | 10x |
| 岗位配置加载 | 每次 5-10ms | 首次 5-10ms | - |

### 预期缓存命中率

假设场景：10 个用户同时模拟面试，每人选择热门岗位（Python后端、Java后端、前端开发）

- **首轮查询**: 10 次 miss（需查询 ES）
- **后续查询**: 大概率命中缓存（同岗位重复查询）
- **预期命中率**: 70-90%

---

## ⚠️ 注意事项

### 1. 缓存不适用的场景

❌ **不缓存动态关键词检索**:
```python
# services/interview_service.py:482-490
# 这个查询基于用户回答提取关键词，每次不同
dynamic_references = knowledge_service.search_related_questions(
    keywords=answer_keywords,  # 每次不同
    position=session.position,
    limit=5
)
```

**原因**: 关键词从用户回答中实时提取，缓存无意义

---

### 2. 随机性保留

虽然缓存了 ES 查询结果（50条题目），但 `random.sample` 仍在每次使用时执行：

```python
# 缓存返回 50 条固定题目
reference_questions = knowledge_service.search_by_position(position, limit=50)

# 每次随机选择 10 条展示给 LLM
import random
sample_questions = random.sample(reference_questions, 10)
```

**这是正确的设计**：
- ✅ 减少 ES 查询次数（缓存原始数据）
- ✅ 保持面试题目多样性（随机采样）

---

### 3. 内存占用

**估算**:
- 每条题目约 500 字节（包含 question、answer、向量等）
- 缓存 128 个岗位，每个 50 条题目
- 总内存占用: `128 × 50 × 500 = 3.2 MB`

**结论**: 内存占用极低，完全可接受

---

### 4. 缓存失效策略

当前实现：**永久缓存 + 手动清除**

**优点**:
- 实现简单
- 性能最优（无 TTL 检查开销）

**缺点**:
- 题库更新后需要手动清除缓存

**未来改进**（可选）:
1. 引入 TTL（如 30 分钟自动过期）
2. 使用 Redis 实现分布式缓存
3. 题库更新时自动触发缓存清除

---

## 🚀 最佳实践

### 1. 监控缓存命中率

定期检查 `/admin/cache-stats`，如果命中率低于 50%，可能需要：
- 增加 `maxsize`（默认 128）
- 检查是否有大量不同岗位查询

### 2. 题库更新流程

```bash
# 1. 更新 Elasticsearch 数据
curl -X POST http://es-host:9200/_refresh

# 2. 清除应用缓存
curl -X POST http://localhost:8003/admin/clear-cache

# 3. 验证缓存已清空
curl http://localhost:8003/admin/cache-stats
```

### 3. 调优 maxsize

如果岗位种类超过 128 个，可以调整：

```python
# services/knowledge_service.py
@lru_cache(maxsize=256)  # 增加缓存大小
def _cached_search_by_position(self, position: str, limit: int) -> tuple:
    ...
```

---

## 📈 未来优化方向

### 短期（已完成）
- ✅ 知识库查询缓存
- ✅ 面试官风格缓存
- ✅ 岗位配置缓存
- ✅ 缓存统计 API

### 中期（待实现）
- ⬜ 用户 VIP 状态缓存（减少数据库查询）
- ⬜ 常见技术词向量缓存（减少 DashScope API 调用）
- ⬜ 面试会话中间状态缓存

### 长期（待评估）
- ⬜ 引入 Redis 分布式缓存
- ⬜ 缓存预热机制（应用启动时加载热门岗位）
- ⬜ 智能缓存淘汰策略（基于访问频率）

---

## 🐛 故障排查

### 问题 1: 缓存命中率低

**症状**: `/admin/cache-stats` 显示 hit_rate < 30%

**可能原因**:
1. 用户选择的岗位非常分散
2. `limit` 参数不一致（缓存键包含 limit）

**解决方案**:
- 统一 `limit` 参数（建议固定为 50）
- 增加 `maxsize`

---

### 问题 2: 题库更新后仍返回旧数据

**症状**: ES 数据已更新，但面试问题仍是旧的

**原因**: 缓存未清除

**解决方案**:
```bash
curl -X POST http://localhost:8003/admin/clear-cache
```

---

### 问题 3: 内存占用过高

**症状**: 应用内存持续增长

**排查步骤**:
1. 检查 `currsize` 是否超过预期
2. 检查是否有大量不同的查询参数
3. 考虑减少 `maxsize` 或清除缓存

---

## 📚 相关文档

- [Python functools.lru_cache 文档](https://docs.python.org/3/library/functools.html#functools.lru_cache)
- [Elasticsearch 性能优化](https://www.elastic.co/guide/en/elasticsearch/reference/current/tune-for-search-speed.html)
- [AI面试系统架构文档](./ARCHITECTURE.md)

---

**更新日期**: 2025-01-13
**维护者**: AI 面试系统开发团队
