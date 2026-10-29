<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import {
  ArrowRight,
  Plus,
  Search,
  Refresh,
  Cpu,
  Box,
  Connection,
  Filter,
} from "@element-plus/icons-vue";
import api, { API_BASE_URL, getAllPages, getImageUrl } from "../services/api";
const route = useRoute();
const router = useRouter();
const products = ref([]);
const categories = ref([]);
const selectedCategory = ref("all");
const sortBy = ref("default");
const inStockOnly = ref(false);
const loading = ref(true);
const errorMessage = ref("");
const adding = ref(null);
const brokenImages = ref(new Set());
const page = ref(1);
let controller;
const pageSize = 8;
const filteredProducts = computed(() => {
  const result = products.value.filter(
    (p) => !inStockOnly.value || p.stock > 0,
  );
  if (sortBy.value === "price_asc")
    result.sort((a, b) => Number(a.price) - Number(b.price));
  if (sortBy.value === "price_desc")
    result.sort((a, b) => Number(b.price) - Number(a.price));
  return result;
});
const visibleProducts = computed(() =>
  filteredProducts.value.slice(
    (page.value - 1) * pageSize,
    page.value * pageSize,
  ),
);
const price = (value) =>
  Number(value || 0).toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
async function loadProducts() {
  controller?.abort();
  controller = new AbortController();
  const signal = controller.signal;
  loading.value = true;
  errorMessage.value = "";
  try {
    const params = {};
    if (route.query.search) params.search = route.query.search;
    if (selectedCategory.value !== "all")
      params.category = selectedCategory.value;
    products.value = await getAllPages(`${API_BASE_URL}/products/`, {
      params,
      signal,
    });
    page.value = 1;
  } catch (error) {
    if (!signal.aborted) errorMessage.value = "暂时无法加载商品，请稍后重试。";
  } finally {
    if (!signal.aborted) loading.value = false;
  }
}
async function loadCategories() {
  try {
    categories.value = await getAllPages(
      `${API_BASE_URL}/products/categories/`,
    );
  } catch {
    ElMessage.warning("分类暂时无法加载，你仍可以浏览全部商品");
  }
}
async function addToCart(product) {
  if (adding.value !== null) return;
  if (!localStorage.getItem("access_token")) {
    ElMessage.info("登录后即可将好物加入购物车");
    router.push({ path: "/login", query: { redirect: route.fullPath } });
    return;
  }
  adding.value = product.id;
  try {
    await api.post(
      `${API_BASE_URL}/cart/add/`,
      { product_id: product.id, quantity: 1 },
      {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      },
    );
    ElMessage.success(`已将「${product.name}」加入购物车`);
  } catch (error) {
    ElMessage.error(error.response?.data?.detail || "加入购物车失败，请重试");
  } finally {
    adding.value = null;
  }
}
function scrollToCollection() {
  document.getElementById("collection")?.scrollIntoView({ behavior: "smooth" });
}
function broken(id) {
  brokenImages.value = new Set([...brokenImages.value, id]);
}
function resetFilters() {
  selectedCategory.value = "all";
  sortBy.value = "default";
  inStockOnly.value = false;
  router.replace({ path: "/", hash: "#collection" });
  loadProducts();
}
watch(() => route.query.search, loadProducts);
watch(selectedCategory, loadProducts);
watch([sortBy, inStockOnly], () => {
  page.value = 1;
});
onMounted(() => {
  loadProducts();
  loadCategories();
});
onUnmounted(() => controller?.abort());
</script>

<template>
  <section class="hero">
    <div class="hero-copy">
      <p class="eyebrow"><span class="status-dot"></span> THE NEXT EVERYDAY</p>
      <h1>好物，<br />让生活<span>进一阶。</span></h1>
      <p class="hero-description">
        从科技灵感到日常所爱，<br />在 ShopHub 发现你的下一件心动好物。
      </p>
      <a href="#collection" class="primary-link"
        >探索精选商品 <el-icon><ArrowRight /></el-icon
      ></a>
      <div class="hero-caption">
        <span>01 — 2026 COLLECTION</span><i></i><span>为好奇心而精选</span>
      </div>
    </div>
    <div class="hero-visual" aria-hidden="true">
      <div class="visual-grid"></div>
      <span class="visual-coordinate">SH / DISCOVERY LAB</span>
      <div class="orbit orbit-one"></div>
      <div class="orbit orbit-two"></div>
      <div class="orbit orbit-three"></div>
      <div class="core-shadow"></div>
      <div class="tech-core">
        <div class="core-top">
          <el-icon><Cpu /></el-icon><span>SH.</span
          ><small>EVERYDAY / UPGRADED</small>
        </div>
      </div>
      <span class="float-label float-top"
        ><span class="status-dot"></span> INSPIRED BY TOMORROW</span
      ><span class="float-label float-bottom"
        ><el-icon><Connection /></el-icon> 连接每一种生活灵感</span
      >
      <div class="visual-bottom">
        <span>DESIGNED TO INSPIRE.</span><span>+ 31.23° N</span>
      </div>
    </div>
  </section>
  <div class="discovery-strip">
    <div>
      <span class="strip-number">01</span
      ><span>精选好物<small>CURATED SELECTION</small></span>
    </div>
    <span class="strip-line"></span>
    <div>
      <span class="strip-number">02</span
      ><span>发现灵感<small>DAILY INSPIRATION</small></span>
    </div>
    <span class="strip-line"></span>
    <div>
      <span class="strip-number">03</span
      ><span>轻松拥有<small>EFFORTLESS SHOPPING</small></span>
    </div>
    <span class="strip-sign"
      >LESS ORDINARY. MORE YOU. <el-icon><ArrowRight /></el-icon
    ></span>
  </div>
  <section
    id="collection"
    class="product-section"
    aria-labelledby="collection-title"
  >
    <div class="section-heading">
      <div>
        <p class="eyebrow">THE CURATED COLLECTION</p>
        <h2 id="collection-title">
          {{
            route.query.search
              ? `搜索「${route.query.search}」`
              : "发现你的下一件好物"
          }}<span class="heading-dot">.</span>
        </h2>
        <p>精心挑选，让每一次选择都值得。</p>
      </div>
      <span class="collection-count">{{
        loading ? "正在发现…" : `${filteredProducts.length} 件好物，等你探索`
      }}</span>
    </div>
    <div class="collection-toolbar">
      <div class="category-tabs" role="group" aria-label="商品分类">
        <button
          :class="{ selected: selectedCategory === 'all' }"
          @click="selectedCategory = 'all'"
        >
          全部好物</button
        ><button
          v-for="category in categories"
          :key="category.id"
          :class="{ selected: selectedCategory === String(category.id) }"
          @click="selectedCategory = String(category.id)"
        >
          {{ category.name }}
        </button>
      </div>
      <div class="sort-control">
        <el-icon><Filter /></el-icon
        ><el-select v-model="sortBy" aria-label="商品排序" style="width: 152px"
          ><el-option label="默认排序" value="default" /><el-option
            label="价格：从低到高"
            value="price_asc" /><el-option
            label="价格：从高到低"
            value="price_desc"
        /></el-select>
      </div>
    </div>
    <div class="collection-meta">
      <span><span class="status-dot"></span> 精选，为你的日常而来</span
      ><el-checkbox v-model="inStockOnly">仅看有货</el-checkbox>
    </div>
    <div
      v-if="loading"
      class="product-grid"
      aria-busy="true"
      aria-label="正在加载商品"
    >
      <div v-for="n in 4" :key="n" class="skeleton-card">
        <div></div>
        <span></span><span></span>
      </div>
    </div>
    <div v-else-if="errorMessage" class="empty-state" role="alert">
      <el-icon :size="38"><Connection /></el-icon>
      <h3>连接暂时中断</h3>
      <p>{{ errorMessage }}</p>
      <el-button :icon="Refresh" @click="loadProducts">重新加载</el-button>
    </div>
    <div v-else-if="!filteredProducts.length" class="empty-state">
      <el-icon :size="38"><Search /></el-icon>
      <h3>还没有找到心动好物</h3>
      <p>试试其他关键词，或查看全部商品。</p>
      <el-button @click="resetFilters">查看全部好物</el-button>
    </div>
    <div v-else class="product-grid">
      <article
        v-for="(product, index) in visibleProducts"
        :key="product.id"
        class="product-card"
      >
        <RouterLink
          :to="`/products/${product.id}`"
          class="product-image"
          :aria-label="`查看 ${product.name}`"
          ><span class="product-index"
            >SH —
            {{
              String((page - 1) * pageSize + index + 1).padStart(2, "0")
            }}</span
          ><img
            v-if="product.image && !brokenImages.has(product.id)"
            :src="getImageUrl(product.image)"
            :alt="product.name"
            loading="lazy"
            @error="broken(product.id)" />
          <div v-else class="image-placeholder">
            <el-icon :size="54"><Box /></el-icon><span>SHOPHUB / SELECTED</span>
          </div>
          <span class="product-image-arrow"
            ><el-icon><ArrowRight /></el-icon></span
        ></RouterLink>
        <div class="product-info">
          <div class="product-meta">
            <span>{{ product.category?.name || "精选好物" }}</span
            ><span :class="product.stock > 0 ? 'available' : 'unavailable'"
              ><i></i>{{ product.stock > 0 ? "现货" : "暂时缺货" }}</span
            >
          </div>
          <RouterLink :to="`/products/${product.id}`" class="product-name">{{
            product.name
          }}</RouterLink>
          <p class="product-description">
            {{ product.description || "探索日常里的新可能。" }}
          </p>
          <div class="product-bottom">
            <span class="price"><small>¥</small>{{ price(product.price) }}</span
            ><el-button
              class="add-button"
              :aria-label="`将 ${product.name} 加入购物车`"
              :disabled="
                product.stock <= 0 || (adding !== null && adding !== product.id)
              "
              :loading="adding === product.id"
              @click="addToCart(product)"
              ><el-icon v-if="adding !== product.id"><Plus /></el-icon
            ></el-button>
          </div>
        </div>
      </article>
    </div>
    <el-pagination
      v-if="!loading && !errorMessage && filteredProducts.length > pageSize"
      v-model:current-page="page"
      :page-size="pageSize"
      :total="filteredProducts.length"
      layout="prev, pager, next"
      class="collection-pagination"
      @current-change="scrollToCollection"
    />
    <div class="collection-end">
      <span></span><el-icon><Cpu /></el-icon>
      <p>GOOD FINDS. GREAT EVERYDAYS.</p>
      <span></span>
    </div>
  </section>
</template>
