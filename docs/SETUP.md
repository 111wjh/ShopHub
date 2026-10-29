# ShopHub 运行与部署指南

本文面向实际运行和维护项目，所有命令默认从仓库根目录开始。项目概览、架构与核心设计见 [项目 README](../README.md)。

## 快速开始

### 1. 准备环境

- Node.js **22.12 或更高版本的 22 系列 / 更高受支持版本**（当前项目已在 22.20 验证）。
- npm、Git。
- Docker Desktop（容器方案）或 Python 3.14（与现有 Dockerfile 一致的本地后端方案）。
- 可访问的 PostgreSQL 实例和 Redis。

**当前 Compose 没有包含 PostgreSQL、Redis 或前端。** 需要单独准备数据库和 Redis，前端使用独立终端运行。

```powershell
git clone https://github.com/111wjh/ShopHub.git
cd ShopHub
```

### 2. 配置后端环境

首次克隆后复制配置示例；已有本地配置时直接检查，不要覆盖：

```powershell
Copy-Item .env.docker.example .env.docker
```

编辑 `.env.docker`：

| 变量                                  | 说明                                                        |
| ------------------------------------- | ----------------------------------------------------------- |
| `DJANGO_SECRET_KEY`                   | 自己生成的 Django 密钥                                      |
| `DJANGO_DEBUG`                        | 本地开发可设 `True`，公开部署需结合后端部署配置             |
| `DB_NAME` / `DB_USER` / `DB_PASSWORD` | 已创建的 PostgreSQL 数据库与账号                            |
| `DB_HOST` / `DB_PORT`                 | Docker Desktop 访问宿主机通常为 `host.docker.internal:5432` |
| `CELERY_BROKER_URL`                   | Redis 消息代理地址                                          |
| `CELERY_RESULT_BACKEND`               | Redis 结果存储地址                                          |

宿主机 PostgreSQL 必须允许来自容器的连接。仓库中的旧 `db.sqlite3` 文件不是当前数据库配置所使用的数据库。

### 3. 启动容器后端与 Redis

推荐让现有 Compose 服务与 Redis 使用同一个 Docker 网络。将 `.env.docker` 中两个 Redis 地址改为：

```dotenv
CELERY_BROKER_URL=redis://shophub-redis:6379/0
CELERY_RESULT_BACKEND=redis://shophub-redis:6379/1
```

启动现有三个服务，指定项目名以固定网络名称：

```powershell
docker compose -p shophub --env-file .env.docker up -d --build
```

首次创建 Redis，接入刚创建的 `shophub_default` 网络：

```powershell
docker run -d --name shophub-redis --restart unless-stopped --network shophub_default redis:7
```

如果 Redis 容器已存在，启动它，并检查是否已经接入网络：

```powershell
docker start shophub-redis
docker network inspect shophub_default
# 仅当网络中尚无该容器时执行：
docker network connect shophub_default shophub-redis
```

Celery 启动时若 Redis 尚未就绪会出现连接重试。Redis 就绪后检查：

```powershell
docker exec shophub-redis redis-cli ping
docker compose -p shophub logs --tail 50 celery
```

预期 Redis 返回 `PONG`，Celery 日志显示连接成功。

### 4. 初始化数据库与商品

```powershell
docker compose -p shophub exec backend python manage.py migrate
docker compose -p shophub exec backend python manage.py createsuperuser
```

访问 [Django Admin](http://localhost:8080/admin/)，使用超级用户登录。先创建分类，再创建商品并设置价格、库存和上架状态。也可在前端以管理员登录后管理商品；分类创建沿用 Django Admin。

仓库不附带生产数据、预置账号或已上传商品图片，第一次启动没有商品是正常情况。

### 5. 启动前端

新开终端：

```powershell
cd frontend
npm ci
npm run dev
```

打开 [ShopHub 本地商城](http://localhost:5173)。默认由 Vite 将 `/api` 和 `/media` 代理至 `http://localhost:8080`。

如果 5173 被其他项目占用，可运行：

```powershell
npm run dev -- --port 5174
```

通过上述相对路径代理访问时，无需为新开发端口修改后端 CORS。

### 可选：本地 Python 后端

不用容器时，先在本机准备 PostgreSQL 与 Redis，然后：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.docker.example .env
```

编辑 `.env`：`DB_HOST=127.0.0.1`，两个 Redis 地址分别使用 `redis://127.0.0.1:6379/0`、`redis://127.0.0.1:6379/1`，并设置自己的数据库账号和密钥。

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8000
```

另开终端启动任务进程（Windows）：

```powershell
.\.venv\Scripts\Activate.ps1
celery -A config worker -l info --pool=solo
```

前端创建 `frontend/.env.local`，写入 `VITE_PROXY_TARGET=http://127.0.0.1:8000`，再启动 Vite。

## 前端配置

可将 `frontend/.env.example` 复制为 `frontend/.env.local`，按需覆盖：

```dotenv
VITE_API_BASE_URL=/api
VITE_MEDIA_BASE_URL=
VITE_PROXY_TARGET=http://localhost:8080
```

| 配置项                | 默认值                  | 作用                                                     |
| --------------------- | ----------------------- | -------------------------------------------------------- |
| `VITE_API_BASE_URL`   | `/api`                  | 浏览器访问的接口前缀，可配置完整 API 地址                |
| `VITE_MEDIA_BASE_URL` | 空                      | `/media/` 图片的来源；API 为完整 URL 时默认使用其 origin |
| `VITE_PROXY_TARGET`   | `http://localhost:8080` | 只用于 Vite 开发和预览服务器的代理目标                   |

修改环境变量后重启 Vite；生产构建需要重新执行 `npm run build`。`VITE_` 变量会进入浏览器代码，只能放可公开的地址和配置。

JWT 访问令牌与刷新令牌沿用原项目的 localStorage 存储方式。遇到接口返回 401 时清理登录状态；再次登录后继续访问。当前没有自动刷新令牌，后端也没有暴露刷新端点。

## API 速查

默认 API 前缀为 `/api`。认证请求携带 `Authorization: Bearer <access_token>`。

| 方法        | 路径                     | 权限 / 用途                                   |
| ----------- | ------------------------ | --------------------------------------------- |
| POST        | `/users/register/`       | 公开；用户名、邮箱、密码                      |
| POST        | `/users/login/`          | 公开；返回 `access`、`refresh`                |
| GET         | `/users/me/`             | 登录用户资料和 `is_staff`                     |
| GET         | `/products/`             | 已上架商品；支持 `search`、`category`、`page` |
| GET         | `/products/categories/`  | 分类列表                                      |
| GET         | `/products/:id/`         | 已上架商品详情                                |
| GET         | `/products/?manage=true` | 管理员查询全部商品                            |
| POST        | `/products/create/`      | 管理员新增；支持 FormData 图片上传            |
| PUT / PATCH | `/products/:id/update/`  | 管理员修改 / 上下架                           |
| DELETE      | `/products/:id/delete/`  | 管理员删除                                    |
| GET         | `/cart/`                 | 当前购物车                                    |
| POST        | `/cart/add/`             | `{ product_id, quantity }`                    |
| PUT         | `/cart/item/:id/`        | `{ quantity }`                                |
| DELETE      | `/cart/item/:id/delete/` | 移除购物车商品                                |
| POST        | `/orders/create/`        | 从整个购物车创建订单                          |
| GET         | `/orders/`               | 当前用户订单；管理员为全部订单                |
| GET         | `/orders/:id/`           | 订单详情                                      |
| POST        | `/orders/:id/pay/`       | 模拟支付                                      |
| POST        | `/orders/:id/cancel/`    | 取消待支付订单                                |
| POST        | `/orders/:id/ship/`      | 管理员发货                                    |
| POST        | `/orders/:id/complete/`  | 确认收货                                      |

路径、字段与权限以项目源码为准。商品图片支持 JPG、PNG、WEBP，最大 5 MB。列表工具兼容普通数组和 DRF 的 `{ count, next, results }` 响应；后端分页会被完整读取，再进行前端价格排序、库存筛选和分页，适合当前项目规模。

## 验证与构建

```powershell
cd frontend
npm test
npm run build
npm run preview
```

- `npm test`：运行分页完整性、鉴权头与筛选参数保留、分页来源、循环分页、错误传播和媒体 URL 测试。
- `npm run build`：编译全部 Vue 页面，输出至 `frontend/dist/`。
- `npm run preview`：本地预览生产构建；使用同样的 `/api`、`/media` 代理。

前端已进行桌面与手机浏览器检查，并使用隔离的内存测试接口验证商品分页、库存筛选、登录返回、购物车数量与金额、下单和模拟支付。模拟接口验证不能替代真实 PostgreSQL、Redis、Celery 与后端的联合验收。

## 部署说明

当前 `docker-compose.yml` 和 `nginx/nginx.conf` **只运行后端与媒体代理，不会构建或托管 Vue 前端**。Vite 的本地代理也不会打包到 `dist/`。

部署前端时：

1. 在 `frontend/` 中执行 `npm ci`、`npm test`、`npm run build`。
2. 将 `frontend/dist/` 托管至静态服务器。
3. 为 Vue Router History 模式配置回退到 `index.html`，避免刷新详情页时 404。
4. 让静态服务器把 `/api/`、`/media/` 代理到现有后端入口，或构建时配置独立 API / 图片来源。
5. 跨来源 API 访问需要由后端允许相应的前端来源。

以下仅为**独立前端 Nginx** 的参考，不是仓库现有配置：

```nginx
server {
    listen 80;
    server_name localhost;
    root /srv/shophub/dist;
    index index.html;

    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $http_host;
    }

    location /media/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $http_host;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

真实公开部署还需结合后端的允许域名、HTTPS、静态文件、密钥、数据库与服务进程配置；现有 Django `runserver` 用于开发。

## 常见问题

| 现象                        | 检查方式                                                               |
| --------------------------- | ---------------------------------------------------------------------- |
| Vite 提示端口被占用         | 使用 `npm run dev -- --port 5174`，或关闭自己已启动的重复进程          |
| 首页显示「连接暂时中断」    | 确认 8080 后端入口可访问，检查 `VITE_PROXY_TARGET`，随后点击重新加载   |
| API 返回 502 / 500          | 检查 backend 日志、PostgreSQL 连接和是否已执行数据库迁移               |
| 首页没有商品                | 在 Admin 创建分类与商品，并设置上架和库存                              |
| 图片 404                    | 检查文件是否在 `media/`，容器媒体挂载及 `VITE_MEDIA_BASE_URL` 是否正确 |
| 登录失效或收到 401          | 重新登录；当前不自动刷新访问令牌                                       |
| 普通用户无法打开商品管理    | 正常权限限制，需使用 `is_staff=True` 的管理员账号                      |
| 超时订单没有自动取消        | 检查 Celery 是否运行、Redis 是否连通，及两个容器是否在同一网络         |
| 刷新 `/products/1` 返回 404 | 静态服务器需要配置 History 模式的 `index.html` 回退                    |
| 修改 `.env.local` 后没生效  | 重启 Vite，或重新构建生产文件                                          |

常用命令：

```powershell
docker compose -p shophub ps
docker compose -p shophub logs --tail 100 backend
docker compose -p shophub logs --tail 100 celery
docker compose -p shophub logs --tail 100 nginx
docker exec shophub-redis redis-cli ping
docker compose -p shophub down
```

最后一条只停止并移除 Compose 管理的容器，不停止单独创建的 Redis。Redis 网络需要在下次启动时重新检查。

## 开发约定与当前边界

- 前端开发说明见 [前端开发说明](../frontend/README.md)；环境速查见 [环境速查](../DEVELOPMENT.md)。
- 不提交 `.env`、`.env.docker`、`.env.local`、令牌、数据库、上传图片、`node_modules` 和 `dist`。
- 当前没有真实支付、物流对接、地址管理、优惠券或真实售后流程。
- 全量读取列表后的前端排序适合小型演示；更大规模商品库需要后端排序和分页能力配合。
- 项目尚未附带开源许可证文件，不能将用途说明视为正式开源授权。
