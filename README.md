# trading_journal

## Docker 开发与运行指南

### 一次性准备
1) 构建镜像（在 `trading_journal/` 目录）：

```bash
docker build -t trading-journal .
```

或使用 Compose（推荐开发）：

```bash
docker compose build
```

2) 初始化数据库（仅首次需要）：

```bash
docker compose run --rm backend python init_db.py
```

### 启动后端（热重载，端口 5000）

```bash
docker compose up backend
```

访问健康检查：
- http://localhost:5000/

常用接口：
- 注册：POST http://localhost:5000/auth/register
- 登录：POST http://localhost:5000/auth/login
- 日志 CRUD：/journals
- 统计：GET http://localhost:5000/stats/summary?user_id=1

### 说明
- Dockerfile 基于 `python:3.11-slim`，在镜像内安装 `backend/requirements.txt`。
- 运行目录为容器内 `/app/backend`，启动命令为 `python -m app.run`（Flask debug 模式，已监听 `0.0.0.0`，支持热重载）。
- Compose 挂载了本地 `backend/` 到容器，代码改动会即时生效；同时单独挂载 `backend/data/` 以持久化 SQLite 数据库。