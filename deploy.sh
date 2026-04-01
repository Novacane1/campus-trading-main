#!/bin/bash
# 校园交易系统 - 服务器部署脚本
set -euo pipefail

echo "=== 校园交易系统部署 ==="

# 1. 启动所有服务
echo "[1/4] 启动 Docker 容器..."
docker compose up -d --build

# 2. 等待数据库就绪
echo "[2/4] 等待数据库就绪..."
until docker compose exec -T db pg_isready -U campus -d campus_trading >/dev/null 2>&1; do
  sleep 2
done

# 3. 初始化数据库
echo "[3/4] 初始化数据库..."
docker compose exec -T backend flask --app run init-db

# 4. 构建推荐模型
echo "[4/4] 构建推荐模型..."
docker compose exec -T backend python scripts/build_recommendation.py

echo ""
echo "=== 部署完成 ==="
echo "前端访问: http://$(hostname -I 2>/dev/null | awk '{print $1}' || echo 'localhost'):80"
echo "后端 API:  http://localhost:5001"
if [ -n "${DEFAULT_ADMIN_PASSWORD:-}" ]; then
  echo "管理员账号: admin / ${DEFAULT_ADMIN_PASSWORD}"
else
  echo "管理员账号: admin"
  echo "管理员密码: 首次初始化时会随机生成并输出；如需固定密码，请在环境变量中设置 DEFAULT_ADMIN_PASSWORD"
fi
