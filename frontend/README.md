# ShopHub 前端

Vue 3 + Vite + Element Plus 电商界面。使用深色背景、冰蓝点缀、CSS 立体芯片视觉、响应式侧栏与统一商品卡片。后端接口保持原项目约定。

## 开发

```powershell
npm ci
npm run dev
```

默认地址为 http://localhost:5173。端口占用时运行 `npm run dev -- --port 5174`。默认代理 `/api`、`/media` 到 `http://localhost:8080`；启动后端的方法见[项目 README](../README.md)。

## 配置

首次需要自定义时，复制 `.env.example` 为 `.env.local`：

```dotenv
VITE_API_BASE_URL=/api
VITE_MEDIA_BASE_URL=
VITE_PROXY_TARGET=http://localhost:8080
```

本地 Django 直接在 8000 运行时，只需把 `VITE_PROXY_TARGET` 改成 `http://127.0.0.1:8000`。环境变量修改后重启 Vite。`VITE_` 配置可被浏览器读取，不存放任何密钥。

## 结构与约定

- `src/App.vue`：全局导航、搜索、用户、购物车计数、移动菜单。
- `src/style.css`：颜色变量、全局与 Element Plus 深色主题、各页面布局、响应式和减少动画偏好。
- `src/router/index.js`：页面、标题、滚动行为、未登录返回路径、管理员守卫。
- `src/services/api.js`：统一 Axios 客户端、15 秒超时、401 处理、接口 / 图片地址。
- `src/services/data.js`：读取完整 DRF 分页、规范化媒体 URL；不依赖 Vue。
- `src/views/`：商城首页、详情、购物车、订单、登录注册、商品管理。
- `tests/data.test.mjs`：无需额外依赖的 Node.js 单元测试。

接口统一从 `services/api` 导入，避免在页面中写死主机。价格、库存、订单状态仍由后端校验。购物车或订单写入成功后客户端派发 `cart-updated`；登录成功或认证失效时派发 `auth-changed`，用于同步公共导航。

首页每页 8 件商品，支持搜索、分类、价格排序、仅看有货和缺图回退。分类数据读取自现有后端，不预设商品或销量。所有后端分页读取完成后再做前端排序与分页；大型数据量需要后端进一步支持。

## 验证

```powershell
npm test
npm run build
npm run preview
```

建议验收：

1. 搜索、分类、排序、现货筛选、下一页、空结果与接口失败重试。
2. 未登录打开购物车后转到登录页，登录后返回购物车。
3. 注册表单校验、注册成功跳转、错误登录提示。
4. 加入购物车、更新数量、移除、总额和导航计数同步。
5. 创建订单、模拟支付、支付时间、取消、发货及确认收货。
6. 普通用户无商品管理入口，管理员可打开并操作商品表单。
7. 1440、390、320 像素宽度下的布局、导航、图片和表格内部滚动。

生产文件输出至 `dist/`。生产服务器需要 History 模式回退，以及独立配置 `/api/`、`/media/` 的代理；开发代理不会进入静态构建。此次浏览器流程验证使用隔离测试接口，真实后端联调需在 PostgreSQL、Redis 和 Celery 就绪后执行。
