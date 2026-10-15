# ShopHub 开发环境说明

## 当前技术栈

- 后端：Django REST Framework
- 前端：Vue 3 + Vite
- 数据库：PostgreSQL
- 缓存与任务队列基础设施：Redis（准备接入 Celery）

## Redis（Docker）

Redis 使用 Docker 容器运行。

- 容器名称：`shophub-redis`
- 镜像：`redis:7`
- 本机地址：`127.0.0.1:6379`

### 启动 Redis

```powershell
docker start shophub-redis
```

### 检查 Redis

```powershell
docker exec shophub-redis redis-cli ping
```

正常结果为 `PONG`。

### 停止 Redis

```powershell
docker stop shophub-redis
```

> 注意：Redis 当前运行在本机，后续接入 Django 和 Celery 时，还需要配置对应的连接地址。
