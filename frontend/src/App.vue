<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage, ElConfigProvider } from "element-plus";
import zhCn from "element-plus/es/locale/lang/zh-cn";
import {
  Search,
  ShoppingCart,
  Grid,
  Tickets,
  Setting,
  ArrowRight,
  SwitchButton,
  User,
  Cpu,
  Close,
  Menu,
} from "@element-plus/icons-vue";
import api, { API_BASE_URL } from "./services/api";
const route = useRoute();
const router = useRouter();
const user = ref(null);
const cartCount = ref(0);
const query = ref("");
const menuOpen = ref(false);
const isAuth = computed(() => ["/login", "/register"].includes(route.path));
const section = computed(() => route.meta.title || "发现好物");
const links = computed(() => [
  { to: "/", label: "探索商城", sub: "Discover", icon: Grid },
  { to: "/cart", label: "购物车", sub: "Your collection", icon: ShoppingCart },
  { to: "/orders", label: "我的订单", sub: "Orders", icon: Tickets },
  ...(user.value?.is_staff
    ? [
        {
          to: "/product-manage",
          label: "商品管理",
          sub: "Workspace",
          icon: Setting,
        },
      ]
    : []),
]);
async function loadUser() {
  if (!localStorage.getItem("access_token")) {
    user.value = null;
    cartCount.value = 0;
    return;
  }
  try {
    user.value = (await api.get(`${API_BASE_URL}/users/me/`, auth())).data;
    await loadCartCount();
  } catch {
    user.value = null;
  }
}
function auth() {
  return {
    headers: {
      Authorization: `Bearer ${localStorage.getItem("access_token")}`,
    },
  };
}
async function loadCartCount() {
  if (!localStorage.getItem("access_token")) {
    cartCount.value = 0;
    return;
  }
  try {
    const { data } = await api.get(`${API_BASE_URL}/cart/`, auth());
    cartCount.value = (data.items || []).reduce(
      (sum, item) => sum + item.quantity,
      0,
    );
  } catch {
    /* The cart page exposes retry and error details. */
  }
}
function logout() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
  user.value = null;
  cartCount.value = 0;
  router.push("/");
  ElMessage.success("已退出登录");
}
function search() {
  router.push({
    path: "/",
    query: query.value.trim() ? { search: query.value.trim() } : {},
    hash: "#collection",
  });
}
function authChanged() {
  if (!localStorage.getItem("access_token")) {
    user.value = null;
    cartCount.value = 0;
    if (route.meta.auth)
      router.replace({ path: "/login", query: { redirect: route.fullPath } });
  } else loadUser();
}
watch(
  () => route.fullPath,
  () => {
    menuOpen.value = false;
    query.value = String(route.query.search || "");
  },
);
onMounted(() => {
  loadUser();
  window.addEventListener("cart-updated", loadCartCount);
  window.addEventListener("auth-changed", authChanged);
});
onUnmounted(() => {
  window.removeEventListener("cart-updated", loadCartCount);
  window.removeEventListener("auth-changed", authChanged);
});
</script>

<template>
  <ElConfigProvider :locale="zhCn">
    <a href="#page-main" class="skip-link">跳转到主要内容</a>
    <header class="app-header">
      <RouterLink to="/" class="brand" aria-label="ShopHub 首页"
        ><span class="brand-symbol"
          ><el-icon><Cpu /></el-icon></span
        >Shop<span>Hub</span><sup>®</sup></RouterLink
      >
      <span class="header-divider"></span
      ><span class="header-caption">CURATED FOR YOUR NEXT.</span>
      <form class="global-search" role="search" @submit.prevent="search">
        <el-icon><Search /></el-icon
        ><input
          v-model="query"
          aria-label="搜索商品"
          placeholder="搜索你的下一件好物…"
        /><button type="submit" aria-label="搜索">
          <el-icon><ArrowRight /></el-icon>
        </button>
      </form>
      <div class="account-actions">
        <template v-if="user"
          ><span class="account-name">{{ user.username }}</span
          ><button class="icon-button" aria-label="退出登录" @click="logout">
            <el-icon><SwitchButton /></el-icon></button></template
        ><RouterLink v-else to="/login" class="account-link"
          ><el-icon><User /></el-icon><span>登录 / 注册</span></RouterLink
        ><RouterLink to="/cart" class="header-cart" aria-label="打开购物车"
          ><el-icon><ShoppingCart /></el-icon
          ><span class="cart-badge">{{ cartCount }}</span></RouterLink
        ><button
          class="icon-button mobile-menu"
          :aria-expanded="menuOpen"
          aria-label="切换导航菜单"
          @click="menuOpen = !menuOpen"
        >
          <el-icon><Close v-if="menuOpen" /><Menu v-else /></el-icon>
        </button>
      </div>
    </header>
    <button
      v-if="menuOpen"
      class="nav-scrim"
      aria-label="关闭菜单"
      @click="menuOpen = false"
    ></button>
    <aside class="sidebar" :class="{ open: menuOpen }">
      <p class="nav-caption">YOUR SHOPPING SPACE</p>
      <nav aria-label="主要导航">
        <RouterLink
          v-for="link in links"
          :key="link.to"
          :to="link.to"
          :class="{
            active:
              link.to === '/'
                ? route.path === '/'
                : route.path.startsWith(link.to),
          }"
          ><el-icon><component :is="link.icon" /></el-icon
          ><span
            >{{ link.label }}<small>{{ link.sub }}</small></span
          ><span v-if="link.to === '/cart' && cartCount" class="nav-count">{{
            cartCount
          }}</span></RouterLink
        >
      </nav>
      <div class="sidebar-note">
        <span class="tiny-label">THE SHOPHUB EDIT</span
        ><span class="note-orbit"
          ><el-icon><Cpu /></el-icon
        ></span>
        <h3>让好物，<br />成为日常。</h3>
        <p>探索灵感，发现属于<br />你的下一种可能。</p>
        <RouterLink to="/#collection"
          >即刻探索 <el-icon><ArrowRight /></el-icon
        ></RouterLink>
      </div>
      <div class="sidebar-bottom">
        <span class="status-dot"></span> DESIGNED FOR DISCOVERY<small
          >ShopHub · 2026</small
        >
      </div>
    </aside>
    <div class="workspace">
      <main id="page-main" tabindex="-1">
        <div class="breadcrumb">
          <span>ShopHub</span><span>/</span><span>{{ section }}</span
          ><span class="edition">THE EVERYDAY UPGRADE — VOL. 01</span>
        </div>
        <section v-if="isAuth" class="auth-intro">
          <p class="eyebrow">YOUR NEXT STARTS HERE</p>
          <h1>好物与灵感，<span>为你而来。</span></h1>
          <p>登录 ShopHub，把喜欢的好物带进生活。</p>
        </section>
        <RouterView :key="route.path" />
      </main>
      <footer class="app-footer">
        <RouterLink to="/" class="footer-brand"
          >ShopHub<span>®</span></RouterLink
        ><span>精选好物，探索每一种可能。</span
        ><small
          >© {{ new Date().getFullYear() }} ShopHub · Built for the
          curious.</small
        >
      </footer>
    </div>
  </ElConfigProvider>
</template>
