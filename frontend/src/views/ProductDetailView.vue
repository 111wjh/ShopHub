
<template>
  <div class="detail-page">
    <header class="detail-header">
      <div class="header-inner">
        <h2 class="logo" @click="router.push('/')">
          Shop<span>Hub</span>
        </h2>
        <el-button plain @click="router.push('/')">
          返回首页
        </el-button>
      </div>
    </header>

    <main class="detail-main">
      <el-button text @click="router.push('/')">
        ← 返回商品列表
      </el-button>

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

      <el-empty
        v-else-if="!product"
        description="商品不存在或暂未上架"
      />

      <section v-else class="product-detail">
        <div class="image-panel">
          <img
            v-if="product.image"
            :src="getImageUrl(product.image)"
            :alt="product.name"
          />
          <div v-else class="image-placeholder">
            <el-icon :size="64"><Goods /></el-icon>
            <span>暂无商品图片</span>
          </div>
        </div>

        <div class="info-panel">
          <p class="category">
            {{ product.category?.name || '精选商品' }}
          </p>

          <h1>{{ product.name }}</h1>

          <p class="description">
            {{ product.description || '暂无商品介绍' }}
          </p>

          <div class="price">
            <span>¥</span>{{ formatPrice(product.price) }}
          </div>

          <p class="stock">
            库存：
            <strong :class="{ empty: product.stock <= 0 }">
              {{ product.stock > 0 ? `${product.stock} 件` : '暂时缺货' }}
            </strong>
          </p>

          <div class="quantity-row">
            <span>购买数量</span>
            <el-input-number
              v-model="quantity"
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Loading, Goods } from '@element-plus/icons-vue'
import axios from 'axios'

const route = useRoute()
const router = useRouter()

const API_BASE_URL = 'http://127.0.0.1:8000/api'

const product = ref(null)
const loading = ref(false)
const adding = ref(false)
const errorMessage = ref('')
const quantity = ref(1)

function formatPrice(price) {
  return Number(price).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}

function getImageUrl(image) {
  if (!image) return ''

  if (image.startsWith('http://') || image.startsWith('https://')) {
    return image
  }

  if (image.startsWith('/media/')) {
    return `http://127.0.0.1:8000${image}`
  }

  return `http://127.0.0.1:8000/media/${image.replace(/^\/+/, '')}`
}

async function loadProduct() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await axios.get(
      `${API_BASE_URL}/products/${route.params.id}/`,
    )
    product.value = response.data
  } catch (error) {
    console.error('加载商品详情失败：', error)

    if (error.response?.status === 404) {
      errorMessage.value = '商品不存在或暂未上架'
    } else {
      errorMessage.value = '商品详情加载失败，请检查后端服务'
    }
  } finally {
    loading.value = false
  }
}

async function addToCart() {
  const token = localStorage.getItem('access_token')

  if (!token) {
    ElMessage.warning('请先登录后再加入购物车')
    router.push('/login')
    return
  }

  if (!product.value || product.value.stock <= 0) {
    ElMessage.warning('该商品暂时缺货')
    return
  }

  if (quantity.value > product.value.stock) {
    ElMessage.warning('购买数量不能超过当前库存')
    return
  }

  adding.value = true

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
    )

    ElMessage.success('已成功加入购物车')
  } catch (error) {
    console.error('加入购物车失败：', error)

    if (error.response?.status === 401) {
      ElMessage.warning('登录状态已失效，请重新登录')
    } else {
      const data = error.response?.data
      const message = data
        ? Object.values(data).flat().join('；')
        : '加入购物车失败，请稍后重试'

      ElMessage.error(message)
    }
  } finally {
    adding.value = false
  }
}

onMounted(() => {
  loadProduct()
})
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  background: #f5f7fa;
  color: #303133;
}

.detail-header {
  background: #fff;
  border-bottom: 1px solid #ebeef5;
}

.header-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 18px 24px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  margin: 0;
  cursor: pointer;
  font-size: 25px;
}

.logo span {
  color: #409eff;
}

.detail-main {
  max-width: 1200px;
  margin: 30px auto;
  padding: 0 24px 50px;
}

.state-area {
  padding: 80px 0;
  text-align: center;
  color: #909399;
}

.product-detail {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 48px;
  margin-top: 20px;
  padding: 32px;
  background: #fff;
  border-radius: 16px;
}

.image-panel {
  min-height: 360px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: #f5f7fa;
  border-radius: 12px;
}

.image-panel img {
  width: 100%;
  max-height: 500px;
  object-fit: contain;
}

.image-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #909399;
}

.info-panel {
  padding: 12px 0;
}

.category {
  color: #409eff;
}

.info-panel h1 {
  margin: 16px 0;
  font-size: 30px;
}

.description {
  min-height: 50px;
  color: #606266;
  line-height: 1.8;
  white-space: pre-wrap;
}

.price {
  margin: 28px 0;
  color: #f56c6c;
  font-size: 36px;
  font-weight: 700;
}

.price span {
  margin-right: 4px;
  font-size: 22px;
}

.stock {
  margin: 20px 0;
  color: #606266;
}

.stock strong {
  color: #67c23a;
}

.stock strong.empty {
  color: #f56c6c;
}

.quantity-row {
  display: flex;
  align-items: center;
  gap: 20px;
  margin: 28px 0;
}

.buy-button {
  width: 220px;
}

@media (max-width: 700px) {
  .detail-main {
    margin-top: 16px;
    padding: 0 12px 30px;
  }

  .product-detail {
    grid-template-columns: 1fr;
    gap: 24px;
    padding: 18px;
  }

  .image-panel {
    min-height: 240px;
  }

  .info-panel h1 {
    font-size: 24px;
  }

  .price {
    font-size: 30px;
  }
}
</style>
