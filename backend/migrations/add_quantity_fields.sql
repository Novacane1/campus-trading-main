-- 添加商品数量和订单数量字段
-- 执行命令: psql -U postgres -d campus_trading -f migrations/add_quantity_fields.sql

-- 1. 给 items 表添加 quantity 字段
ALTER TABLE items ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1;

-- 2. 给现有商品设置默认数量为1
UPDATE items SET quantity = 1 WHERE quantity IS NULL;

-- 3. 给 orders 表添加 quantity 字段
ALTER TABLE orders ADD COLUMN IF NOT EXISTS quantity INTEGER DEFAULT 1;

-- 4. 给现有订单设置默认数量为1
UPDATE orders SET quantity = 1 WHERE quantity IS NULL;

-- 5. 验证
SELECT 'Items table updated' AS status, COUNT(*) AS total_items FROM items;
SELECT 'Orders table updated' AS status, COUNT(*) AS total_orders FROM orders;

