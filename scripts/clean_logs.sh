#!/bin/bash
#
# 日志清理脚本
# 功能：删除超过指定天数的旧日志文件
#
# 使用方法：
#   ./scripts/clean_logs.sh           # 删除30天前的日志（默认）
#   ./scripts/clean_logs.sh 7         # 删除7天前的日志
#
# 建议通过 crontab 定期执行：
#   0 2 * * * /path/to/clean_logs.sh  # 每天凌晨2点执行
#

# 日志目录
LOG_DIR="$(cd "$(dirname "$0")/.." && pwd)/logs"

# 保留天数（默认30天）
RETENTION_DAYS=${1:-30}

echo "================================================"
echo "日志清理脚本"
echo "================================================"
echo "日志目录: $LOG_DIR"
echo "保留天数: $RETENTION_DAYS 天"
echo "开始时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 检查目录是否存在
if [ ! -d "$LOG_DIR" ]; then
    echo "❌ 错误：日志目录不存在: $LOG_DIR"
    exit 1
fi

# 统计清理前的文件数和大小
BEFORE_COUNT=$(find "$LOG_DIR" -type f -name "*.log*" | wc -l)
BEFORE_SIZE=$(du -sh "$LOG_DIR" 2>/dev/null | awk '{print $1}')

echo "清理前："
echo "  文件数量: $BEFORE_COUNT"
echo "  总大小: $BEFORE_SIZE"
echo ""

# 查找并删除旧日志文件
echo "正在清理 ${RETENTION_DAYS} 天前的日志文件..."

# 删除 .log.YYYY-MM-DD 格式的轮转日志
DELETED_COUNT=0
while IFS= read -r -d '' file; do
    echo "  删除: $file"
    rm -f "$file"
    ((DELETED_COUNT++))
done < <(find "$LOG_DIR" -type f -name "*.log.*" -mtime +${RETENTION_DAYS} -print0)

echo ""
echo "清理完成："
echo "  已删除文件: $DELETED_COUNT 个"

# 统计清理后的文件数和大小
AFTER_COUNT=$(find "$LOG_DIR" -type f -name "*.log*" | wc -l)
AFTER_SIZE=$(du -sh "$LOG_DIR" 2>/dev/null | awk '{print $1}')

echo "  剩余文件: $AFTER_COUNT 个"
echo "  当前大小: $AFTER_SIZE"
echo ""
echo "结束时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================"

# 返回删除的文件数
exit 0
