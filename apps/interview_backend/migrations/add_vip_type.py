"""添加vip_type字段到User表

使用方法：
    python migrations/add_vip_type.py
"""
import sys
import os

# 添加父目录到路径以导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import engine, SessionLocal
from sqlalchemy import text


def migrate():
    """执行迁移"""
    db = SessionLocal()

    try:
        print("[迁移] 开始添加vip_type字段...")

        # 检查字段是否已存在
        result = db.execute(text("PRAGMA table_info(users)"))
        columns = [row[1] for row in result.fetchall()]

        if 'vip_type' in columns:
            print("[迁移] vip_type字段已存在，跳过迁移")
            return

        # SQLite不支持直接ALTER TABLE ADD COLUMN with DEFAULT，需要分步进行
        print("[迁移] 添加vip_type字段...")
        db.execute(text("ALTER TABLE users ADD COLUMN vip_type VARCHAR(20)"))
        db.commit()

        # 数据迁移：将is_vip=True的用户设置为super类型（向下兼容）
        print("[迁移] 迁移现有VIP用户数据...")
        db.execute(text("""
            UPDATE users
            SET vip_type = 'super'
            WHERE is_vip = 1
        """))
        db.commit()

        print("[迁移] 迁移完成！")
        print("[迁移] - 已添加vip_type字段")
        print("[迁移] - 已迁移现有VIP用户为超级VIP")

    except Exception as e:
        print(f"[迁移] 迁移失败: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    migrate()
