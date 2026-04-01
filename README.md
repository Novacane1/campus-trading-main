# Campus Trading System

一个面向校园场景的二手交易平台，包含前台商城、用户中心、后台管理、推荐系统、时空匹配，以及支付宝沙箱支付接入。

## Tech Stack

- Frontend: Vue 3 + Vite + Element Plus + Pinia
- Backend: Flask + SQLAlchemy + Flask-JWT-Extended
- Database: PostgreSQL
- Cache: Redis
- Deployment: Docker Compose + Nginx

## Project Structure

```text
.
├── backend/                Flask backend
├── frontend/               Vue frontend
├── docker-compose.yml      One-command local/server deployment
├── deploy.sh               Deployment bootstrap script
├── .env.example            Root environment template
└── backend/.env.example    Backend-only environment template
```

## Features

- 用户注册、登录、资料管理、收藏、历史记录
- 商品发布、搜索、分类浏览、购物车、订单、评价
- 后台管理、审核、日志、统计面板
- 推荐系统与 embedding 构建脚本
- 时空匹配与推荐面交方案
- 支付宝沙箱网页支付

## Quick Start

### 1. Prepare environment

复制环境变量模板：

```bash
cp .env.example .env
```

按需修改 `.env` 中的配置，至少建议设置：

- `SECRET_KEY`
- `JWT_SECRET_KEY`
- `DB_PASSWORD`
- `DEFAULT_ADMIN_PASSWORD`

如果要联调支付宝沙箱，还需要填写：

- `ALIPAY_APP_ID`
- `ALIPAY_APP_PRIVATE_KEY`
- `ALIPAY_PUBLIC_KEY`
- `ALIPAY_NOTIFY_URL`
- `ALIPAY_RETURN_URL`

### 2. Start services

```bash
docker compose up -d --build
```

### 3. Initialize database

```bash
docker compose exec -T backend flask --app run init-db
```

如果没有设置 `DEFAULT_ADMIN_PASSWORD`，初始化时会自动生成随机管理员密码，并在命令输出中打印。

### 4. Build recommendation artifacts

```bash
docker compose exec -T backend python scripts/build_recommendation.py
```

### 5. Open the app

- Frontend: `http://localhost/`
- Backend API: `http://localhost:5001/`

## One-Command Deployment

项目提供了部署脚本：

```bash
bash deploy.sh
```

这个脚本会：

1. 构建并启动容器
2. 等待数据库就绪
3. 初始化数据库
4. 构建推荐模型

## Common Commands

查看服务状态：

```bash
docker compose ps
```

查看日志：

```bash
docker compose logs -f backend frontend
```

停止服务：

```bash
docker compose down
```

重新构建推荐数据：

```bash
docker compose exec -T backend python scripts/build_recommendation.py
```
