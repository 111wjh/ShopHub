# ShopHub 开发环境速查

完整安装、数据库初始化、接口和部署说明见 [README.md](README.md)。前端维护说明见 [frontend/README.md](frontend/README.md)。

## 前端

```powershell
cd frontend
npm ci
npm run dev
npm test
npm run build
```

默认 5173，端口占用时使用 `npm run dev -- --port 5174`。开发代理默认将 `/api`、`/media` 发往 8080；直接连接本地 Django 时，在 `frontend/.env.local` 中配置 `VITE_PROXY_TARGET=http://127.0.0.1:8000`。

## 既有后端

- PostgreSQL 通过 `.env`（本地）或 `.env.docker`（容器）配置。
- Compose 只有 backend、celery、nginx；PostgreSQL 与 Redis 需独立准备。
- API / 媒体代理默认 8080；Django 直连 8000。
- Celery 已接入，处理约 15 分钟后的待支付订单超时检查。
- Redis 必须可从 Celery 访问；容器内的 localhost 指向容器自己。

```powershell
docker compose -p shophub ps
docker compose -p shophub logs --tail 50 backend
docker compose -p shophub logs --tail 50 celery
docker exec shophub-redis redis-cli ping
```

不将本地环境变量、数据库、媒体文件或构建目录提交到 Git。前端改动只调整表现、客户端交互与接口调用，不更改后端业务规则。
