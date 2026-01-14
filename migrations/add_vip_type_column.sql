-- 添加 vip_type 字段到 users 表
-- 执行时间: 2026-01-14
-- 说明: 添加 vip_type 字段以支持多层级VIP系统（普通用户、普通VIP、超级VIP）

-- 添加 vip_type 列（如果不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name = 'users'
        AND column_name = 'vip_type'
    ) THEN
        ALTER TABLE users ADD COLUMN vip_type VARCHAR(20);
        RAISE NOTICE 'vip_type 字段已添加';
    ELSE
        RAISE NOTICE 'vip_type 字段已存在，跳过';
    END IF;
END $$;

-- 为现有的VIP用户设置默认值
-- is_vip=true 的用户设置为 'normal' VIP
UPDATE users
SET vip_type = 'normal'
WHERE is_vip = true AND vip_type IS NULL;

-- 为普通用户设置 NULL（可选，因为默认就是 NULL）
-- UPDATE users
-- SET vip_type = NULL
-- WHERE is_vip = false AND vip_type IS NOT NULL;

-- 验证结果
SELECT
    COUNT(*) as total_users,
    COUNT(CASE WHEN vip_type = 'normal' THEN 1 END) as normal_vip_count,
    COUNT(CASE WHEN vip_type = 'super' THEN 1 END) as super_vip_count,
    COUNT(CASE WHEN vip_type IS NULL THEN 1 END) as regular_user_count
FROM users;
