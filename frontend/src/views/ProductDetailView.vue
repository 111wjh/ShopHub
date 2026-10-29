<template>
  <div class="detail-page">
    <main class="detail-main">
      <el-button text @click="router.push('/')"> ← 返回商品列表 </el-button>

      <div v-if="loading" class="state-area">
        <el-icon class="is-loading" :size="32">
          <Loading />
        </el-icon>
        <p>正在加载商品详情...</p>
      </div>

      <el-alert
        v-else-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        :closable="false"
      />

      <el-empty v-else-if="!product" description="商品不存在或暂未上架" />

      <section v-else class="product-detail">
        <div class="image-panel">
          <img
            v-if="product.image && !imageFailed"
            :src="getImageUrl(product.image)"
            :alt="product.name"
            @error="imageFailed = true"
          />
          <div v-else class="image-placeholder">
            <el-icon :size="64"><Goods /></el-icon>
            <span>暂无商品图片</span>
          </div>
        </div>

        <div class="info-panel">
          <p class="category">
            {{ product.category?.name || "精选商品" }}
          </p>

          <h1>{{ product.name }}</h1>

          <p class="description">
            {{ product.description || "暂无商品介绍" }}
          </p>

          <div class="price">
            <span>¥</span>{{ formatPrice(product.price) }}
          </div>

          <p class="stock">
            库存：
            <strong :class="{ empty: product.stock <= 0 }">
              {{ product.stock > 0 ? `${product.stock} 件` : "暂时缺货" }}
            </strong>
          </p>

          <div class="quantity-row">
            <span>购买数量</span>
            <el-input-number
              v-model="quantity"
              :precision="0"
              :step-strictly="true"
              :min="1"
              :max="Math.max(1, product.stock)"
              :disabled="product.stock <= 0"
            />
          </div>

          <el-button
            type="primary"
            size="large"
            class="buy-button"
            :disabled="product.stock <= 0"
            :loading="adding"
            @click="addToCart"
          >
            加入购物车
          </el-button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useRoute, useRouter } from "vue-router";
import { ElMessage } from "element-plus";
import { Loading, Goods } from "@element-plus/icons-vue";
import axios, { API_BASE_URL, getImageUrl } from "../services/api";

const route = useRoute();
const router = useRouter();

const product = ref(null);
const loading = ref(false);
const adding = ref(false);
const errorMessage = ref("");
const quantity = ref(1);
const imageFailed = ref(false);

function formatPrice(price) {
  return Number(price).toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

async function loadProduct() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await axios.get(
      `${API_BASE_URL}/products/${route.params.id}/`,
    );
    product.value = response.data;
  } catch (error) {
    console.error("加载商品详情失败：", error);

    if (error.response?.status === 404) {
      errorMessage.value = "商品不存在或暂未上架";
    } else {
      errorMessage.value = "商品详情加载失败，请检查后端服务";
    }
  } finally {
    loading.value = false;
  }
}

async function addToCart() {
  if (adding.value) return;
  const token = localStorage.getItem("access_token");

  if (!token) {
    ElMessage.warning("请先登录后再加入购物车");
    router.push({ path: "/login", query: { redirect: route.fullPath } });
    return;
  }

  if (!product.value || product.value.stock <= 0) {
    ElMessage.warning("该商品暂时缺货");
    return;
  }

  if (
    !Number.isInteger(quantity.value) ||
    quantity.value < 1 ||
    quantity.value > product.value.stock
  ) {
    ElMessage.warning("请输入库存范围内的正整数数量");
    return;
  }

  adding.value = true;

  try {
    await axios.post(
      `${API_BASE_URL}/cart/add/`,
      {
        product_id: product.value.id,
        quantity: quantity.value,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    ElMessage.success("已成功加入购物车");
  } catch (error) {
    console.error("加入购物车失败：", error);

    if (error.response?.status === 401) {
      ElMessage.warning("登录状态已失效，请重新登录");
    } else {
      const data = error.response?.data;
      const message = data
        ? Object.values(data).flat().join("；")
        : "加入购物车失败，请稍后重试";

      ElMessage.error(message);
    }
  } finally {
    adding.value = false;
  }
}

onMounted(() => {
  loadProduct();
});
</script>
