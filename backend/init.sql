-- 电商AIGC商品图合规溯源存证平台 - 数据库初始化
-- 此文件在 PostgreSQL 容器启动时自动执行

-- 创建扩展
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 插入测试商家数据
INSERT INTO merchants (name, phone, email) VALUES
    ('测试商家A', '13800138000', 'merchant_a@test.com'),
    ('测试商家B', '13800138001', 'merchant_b@test.com'),
    ('数码旗舰店', '13800138002', 'digital@store.com')
ON CONFLICT DO NOTHING;
