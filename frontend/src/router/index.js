import { createRouter, createWebHistory } from "vue-router";
import api, { API_BASE_URL } from "../services/api";
const routes = [
  {
    path: "/",
    name: "home",
    component: () => import("../views/HomeView.vue"),
    meta: { title: "探索商城" },
  },
  {
    path: "/register",
    name: "register",
    component: () => import("../views/RegisterView.vue"),
    meta: { title: "创建账号" },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("../views/LoginView.vue"),
    meta: { title: "欢迎回来" },
  },
  {
    path: "/cart",
    name: "cart",
    component: () => import("../views/CartView.vue"),
    meta: { title: "购物车", auth: true },
  },
  {
    path: "/orders",
    name: "order-list",
    component: () => import("../views/OrderListView.vue"),
    meta: { title: "我的订单", auth: true },
  },
  {
    path: "/orders/:id",
    name: "order-detail",
    component: () => import("../views/OrderDetailView.vue"),
    meta: { title: "订单详情", auth: true },
  },
  {
    path: "/product-manage",
    name: "ProductManage",
    component: () => import("../views/ProductManageView.vue"),
    meta: { title: "商品管理", auth: true, staff: true },
  },
  {
    path: "/products/:id",
    name: "product-detail",
    component: () => import("../views/ProductDetailView.vue"),
    meta: { title: "商品详情" },
  },
  { path: "/:pathMatch(.*)*", redirect: "/" },
];
const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, saved) {
    return (
      saved ||
      (to.hash ? { el: to.hash, top: 100, behavior: "smooth" } : { top: 0 })
    );
  },
});
router.beforeEach(async (to) => {
  const token = localStorage.getItem("access_token");
  if (to.meta.auth && !token)
    return { path: "/login", query: { redirect: to.fullPath } };
  if (to.meta.staff) {
    try {
      const { data } = await api.get(`${API_BASE_URL}/users/me/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!data.is_staff) return "/";
    } catch {
      return { path: "/login", query: { redirect: to.fullPath } };
    }
  }
});
router.afterEach((to) => {
  document.title = `${to.meta.title || "精选好物"} · ShopHub`;
});
export default router;
