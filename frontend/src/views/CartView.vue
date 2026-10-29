<template>
  <div class="cart-page">
    <main class="cart-content">
      <el-card shadow="never">
        <div class="section-title">
          <h2>购物车商品</h2>
          <el-button :loading="loading" @click="loadCart"> 刷新 </el-button>
        </div>

        <el-alert
          v-if="errorMessage"
          :title="errorMessage"
          type="error"
          show-icon
          :closable="false"
          class="error-alert"
        />
        <el-button v-if="errorMessage && !loading" @click="loadCart"
          >重新加载购物车</el-button
        >

        <div v-if="loading" class="loading-area">
          <el-icon class="is-loading" :size="28"><Loading /></el-icon>
          <p>正在加载购物车...</p>
        </div>

        <el-empty
          v-else-if="!errorMessage && items.length === 0"
          description="购物车还是空的，去挑选一些商品吧"
        >
          <el-button type="primary" @click="$router.push('/')">
            去逛逛
          </el-button>
        </el-empty>

        <template v-else-if="!errorMessage">
          <div class="cart-list">
            <article v-for="item in items" :key="item.id" class="cart-item">
              <div class="item-image">
                <img
                  v-if="item.product?.image"
                  :src="getImageUrl(item.product.image)"
                  :alt="item.product.name"
                />
                <el-icon v-else :size="32"><Goods /></el-icon>
              </div>

              <div class="item-info">
                <h3>{{ item.product?.name || "商品" }}</h3>
                <p class="unit-price">
                  单价：¥{{ formatPrice(item.product?.price) }}
                </p>
                <p class="subtotal">小计：¥{{ formatPrice(item.subtotal) }}</p>
              </div>

              <div class="item-actions">
                <el-input-number
                  :model-value="item.quantity"
                  :min="1"
                  :precision="0"
                  :step-strictly="true"
                  :max="Math.max(1, item.product?.stock || 1)"
                  :disabled="
                    updatingId !== null ||
                    deletingId !== null ||
                    creatingOrder ||
                    !item.product?.is_active ||
                    item.product?.stock <= 0
                  "
                  @change="(value) => updateQuantity(item, value)"
                />

                <el-button
                  type="danger"
                  plain
                  :loading="deletingId === item.id"
                  :disabled="
                    updatingId !== null || deletingId !== null || creatingOrder
                  "
                  @click="removeItem(item)"
                >
                  删除
                </el-button>
              </div>
            </article>
          </div>

          <div class="cart-summary">
            <div>
              <p>共 {{ items.length }} 种商品</p>
              <h2>
                合计：
                <span>¥{{ formatPrice(cartTotal) }}</span>
              </h2>
            </div>

            <el-button
              type="primary"
              size="large"
              :loading="creatingOrder"
              :disabled="updatingId !== null || deletingId !== null"
              @click="createOrder"
            >
              创建订单
            </el-button>
          </div>
        </template>
      </el-card>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import axios, { API_BASE_URL, getImageUrl } from "../services/api";
import { ElMessage, ElMessageBox } from "element-plus";
import { Loading, Goods } from "@element-plus/icons-vue";
import { useRouter } from "vue-router";

const router = useRouter();

const items = ref([]);
const cartTotalFromAPI = ref(null);
const loading = ref(false);
const errorMessage = ref("");
const updatingId = ref(null);
const deletingId = ref(null);
const creatingOrder = ref(false);
// cartTotal是自动计算的总价
const cartTotal = computed(() => {
  // 如果后端已经返回了总金额，直接用后端的
  if (cartTotalFromAPI.value !== null) {
    return cartTotalFromAPI.value;
  }
  // 后端没给的话，自己把所有商品的小计加起来
  // reduce是数组求和的方法
  return items.value.reduce((sum, item) => sum + Number(item.subtotal || 0), 0);
});

function formatPrice(price) {
  // 把价格转成数字，空的话就用0
  return Number(price || 0).toLocaleString("zh-CN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  });
}

function getAuthConfig() {
  const token = localStorage.getItem("access_token");

  if (!token) {
    ElMessage.warning("请先登录");
    router.push("/login");
    return null;
  }

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  };
}

async function loadCart() {
  const config = getAuthConfig();
  if (!config) return;

  loading.value = true;
  errorMessage.value = "";

  try {
    const response = await axios.get(`${API_BASE_URL}/cart/`, config);
    const data = response.data;

    items.value = Array.isArray(data.items) ? data.items : [];
    cartTotalFromAPI.value = data.total_amount ?? null;
  } catch (error) {
    console.error("加载购物车失败：", error);
    errorMessage.value = "购物车加载失败，请稍后重试。";
  } finally {
    loading.value = false;
  }
}

async function updateQuantity(item, quantity) {
  // 数量是空的，直接不处理
  if (quantity === null || quantity === undefined) return;
  // 数量没变化，也不发请求
  if (quantity === item.quantity) return;
  if (!Number.isInteger(quantity) || quantity < 1) return;

  const config = getAuthConfig();
  if (!config) return;

  updatingId.value = item.id;

  try {
    await axios.put(
      `${API_BASE_URL}/cart/item/${item.id}/`,
      { quantity },
      config,
    );

    ElMessage.success("商品数量已更新");
    // 重新加载购物车，刷新最新数据
    await loadCart();
  } catch (error) {
    console.error("更新购物车失败：", error);
    const data = error.response?.data;
    const message = data
      ? Object.values(data).flat().join("；")
      : "更新失败，请检查商品库存或重试";

    ElMessage.error(message);
    await loadCart();
  } finally {
    updatingId.value = null;
  }
}

async function removeItem(item) {
  try {
    await ElMessageBox.confirm(
      `确定要删除「${item.product?.name || "该商品"}」吗？`,
      "删除商品",
      {
        confirmButtonText: "确定删除",
        cancelButtonText: "取消",
        type: "warning",
      },
    );
  } catch {
    return;
  }

  const config = getAuthConfig();
  if (!config) return;

  deletingId.value = item.id;

  try {
    await axios.delete(`${API_BASE_URL}/cart/item/${item.id}/delete/`, config);

    ElMessage.success("商品已删除");
    await loadCart();
  } catch (error) {
    console.error("删除购物车商品失败：", error);
    ElMessage.error("删除失败，请重试");
  } finally {
    deletingId.value = null;
  }
}

async function createOrder() {
  if (items.value.length === 0) {
    ElMessage.warning("购物车为空，无法创建订单");
    return;
  }

  try {
    await ElMessageBox.confirm(
      `确认创建订单？当前商品总金额为 ¥${formatPrice(cartTotal.value)}。`,
      "确认订单",
      {
        confirmButtonText: "确认创建",
        cancelButtonText: "再检查一下",
        type: "info",
      },
    );
  } catch {
    // 点取消就不执行
    return;
  }

  const config = getAuthConfig();
  if (!config) return;

  creatingOrder.value = true;

  try {
    const response = await axios.post(
      `${API_BASE_URL}/orders/create/`,
      {},
      config,
    );

    ElMessage.success("订单创建成功");
    router.push(`/orders/${response.data.id}`);
  } catch (error) {
    console.error("创建订单失败：", error);

    const data = error.response?.data;
    const message = data
      ? Object.values(data).flat().join("；")
      : "创建订单失败，请检查后端服务";

    ElMessage.error(message);
  } finally {
    creatingOrder.value = false;
  }
}

onMounted(loadCart);
</script>
