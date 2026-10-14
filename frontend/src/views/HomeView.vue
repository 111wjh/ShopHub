
<template>
  <div class="shop-page">
    <header class="shop-header">
      <div class="header-inner">
        <div class="logo">Shop<span>Hub</span></div>

        <div class="search-box">
          <el-input
            v-model="keyword"
            placeholder="搜索你喜欢的商品"
            clearable
            @keyup.enter="searchProducts"
          />
          <el-button type="primary" @click="searchProducts">
            搜索
          </el-button>
        </div>

        <div class="header-actions">
          <template v-if="user">
            <span class="welcome-user">
              你好，{{ user.username }}
            </span>
            <el-button plain @click="logout">
              退出登录
            </el-button>
          </template>

          <template v-else>
            <el-button plain @click="goLogin">
              登录
            </el-button>
            <el-button type="primary" @click="goRegister">
              注册
            </el-button>
          </template>

          <el-button plain @click="goCart">
            <el-icon><ShoppingCart /></el-icon>
            购物车
          </el-button>
          <el-button plain @click="goOrders">
            我的订单
          </el-button>

          <el-button
            v-if="user && user.is_staff"
            type="primary"
            plain
            @click="goProductManage"
          >
            商品管理
          </el-button>
        </div>

      </div>
    </header>

    <main class="main-content">
      <section class="welcome-banner">
        <div>
          <p class="banner-tag">SHOPHUB ONLINE STORE</p>
          <h1>发现好物，<br />让生活更简单。</h1>
          <p class="banner-desc">
            精选商品 · 简单购物 · 安心体验
          </p>
          <el-button type="primary" size="large" @click="loadProducts">
            浏览商品
          </el-button>
        </div>
        <div class="banner-decoration">S</div>
      </section>

      <section class="product-section">
        <div class="section-heading">
          <div>
            <h2>精选商品</h2>
            <p>为你挑选的优质好物</p>
          </div>
          <span class="product-count">共 {{ products.length }} 件商品</span>
        </div>
        <!-- 商品分类筛选 -->
        <div class="category-filter">
          <!-- 商品排序 -->
          <div class="sort-bar">
            <span>商品排序：</span>

            <el-select
              v-model="sortBy"
              placeholder="请选择排序方式"
              style="width: 180px"
              @change="searchProducts"
            >
              <el-option label="默认排序" value="default" />
              <el-option label="价格从低到高" value="price_asc" />
              <el-option label="价格从高到低" value="price_desc" />
            </el-select>
          </div>
          <el-radio-group
            v-model="selectedCategory"
            @change="searchProducts"
          >
            <el-radio-button label="全部分类" value="all" />

            <el-radio-button
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="String(category.id)"
            />
          </el-radio-group>
        </div>

        <el-alert
          v-if="errorMessage"
          :title="errorMessage"
          type="error"
          show-icon
          :closable="false"
        />

        <div v-if="loading" class="loading-area">
          <el-icon class="is-loading" :size="28"><Loading /></el-icon>
          <p>正在加载商品...</p>
        </div>

        <el-empty
          v-else-if="products.length === 0"
          description="暂时没有找到商品"
        />

        <div v-else class="product-grid">
          <article
            v-for="product in sortedProducts"
            :key="product.id"
            class="product-card"
            @click="goProductDetail(product.id)"
          >
            <div class="product-image">
              <img
                v-if="product.image"
                :src="getImageUrl(product.image)"
                :alt="product.name"
              />
              <div v-else class="image-placeholder">
                <el-icon :size="42"><Goods /></el-icon>
                <span>ShopHub</span>
              </div>
              <span class="stock-tag" :class="{ 'out-of-stock': product.stock <= 0 }">
                {{ product.stock > 0 ? '有库存' : '暂时缺货' }}
              </span>
            </div>

            <div class="product-info">
              <p class="category-name">
                {{ product.category?.name || '精选商品' }}
              </p>
              <h3>{{ product.name }}</h3>
              <p class="product-description">
                {{ product.description || '优质商品，值得拥有。' }}
              </p>

              <div class="product-bottom">
                <span class="price">
                  <small>¥</small>{{ formatPrice(product.price) }}
                </span>
                <el-button
                  type="primary"
                  circle
                  :disabled="product.stock <= 0"
                  @click.stop="addToCart(product)"
                >
                  <el-icon><Plus /></el-icon>
                </el-button>
              </div>
            </div>
          </article>
        </div>
      </section>
    </main>

    <footer class="shop-footer">
      <p>© 2026 ShopHub · 让购物更简单</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'
import {
  ShoppingCart,
  Loading,
  Goods,
  Plus,
} from '@element-plus/icons-vue'
import axios from 'axios'

const router = useRouter()

const keyword = ref('')
const products = ref([])
const loading = ref(false)
const errorMessage = ref('')
// 商品分类列表
const categories = ref([])

// 当前选中的分类，all 表示全部分类
const selectedCategory = ref('all')
// 当前商品排序方式
const sortBy = ref('default')

// 根据选择的方式对商品排序
const sortedProducts = computed(() => {
  const result = [...products.value]

  if (sortBy.value === 'price_asc') {
    result.sort((a, b) => Number(a.price) - Number(b.price))
  } else if (sortBy.value === 'price_desc') {
    result.sort((a, b) => Number(b.price) - Number(a.price))
  }

  return result
})
// 当前登录用户；未登录时为 null
const user = ref(null)

const API_BASE_URL = 'http://127.0.0.1:8000/api'

// 获取当前登录用户
async function loadCurrentUser() {
  const token = localStorage.getItem('access_token')

  if (!token) {
    user.value = null
    return
  }

  try {
    const response = await axios.get(`${API_BASE_URL}/users/me/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    })

    user.value = response.data
  } catch (error) {
    console.error('获取用户信息失败：', error)

    // 令牌无效或过期时，清除登录状态
    user.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }
}

// 跳转登录页面
function goLogin() {
  router.push('/login')
}

// 跳转注册页面
function goRegister() {
  router.push('/register')
}

// 退出登录
function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  user.value = null

  ElMessage.success('已退出登录')
}


function formatPrice(price) {
  return Number(price).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })
}


function getImageUrl(image) {
  if (!image) {
    return ''
  }

  // 后端已经返回完整 URL 时，直接使用
  if (image.startsWith('http://') || image.startsWith('https://')) {
    return image
  }

  // 后端返回 /media/products/xxx.jpg 这样的路径
  if (image.startsWith('/media/')) {
    return `http://127.0.0.1:8000${image}`
  }

  // 兼容 products/xxx.jpg 或其他相对路径
  return `http://127.0.0.1:8000/media/${image.replace(/^\/+/, '')}`
}


async function loadProducts() {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await axios.get(`${API_BASE_URL}/products/`)
    const data = response.data

    // 同时兼容普通数组和 DRF 分页响应
    products.value = Array.isArray(data) ? data : (data.results || [])
  } catch (error) {
    console.error('加载商品失败：', error)
    errorMessage.value = '商品加载失败，请检查 Django 后端是否正在运行。'
  } finally {
    loading.value = false
  }
}

// 获取商品分类
async function loadCategories() {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/products/categories/`
    )

    const data = response.data

    categories.value = Array.isArray(data)
      ? data
      : (data.results || [])
  } catch (error) {
    console.error('加载商品分类失败：', error)
    ElMessage.error('商品分类加载失败')
  }
}

async function searchProducts() {
  loading.value = true
  errorMessage.value = ''

  try {
    const params = {}
    if (keyword.value.trim()) {
      params.search = keyword.value.trim()
    }
    // 添加商品分类条件
    if (selectedCategory.value !== 'all') {
      params.category = selectedCategory.value
    }
    const response = await axios.get(`${API_BASE_URL}/products/`, { params })
    const data = response.data
    products.value = Array.isArray(data) ? data : (data.results || [])
  } catch (error) {
    console.error('搜索商品失败：', error)
    errorMessage.value = '搜索失败，请检查后端接口。'
  } finally {
    loading.value = false
  }
}


async function addToCart(product) {
  const token = localStorage.getItem('access_token')

  // 未登录时，引导用户先登录
  if (!token) {
    ElMessage.warning('请先登录后再加入购物车')
    router.push('/login')
    return
  }

  try {
    await axios.post(
      `${API_BASE_URL}/cart/add/`,
      {
        product_id: product.id,
        quantity: 1,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    )

    ElMessage.success(`已将「${product.name}」加入购物车`)
  } catch (error) {
    console.error('加入购物车失败：', error)

    if (error.response?.status === 401) {
      ElMessage.warning('登录状态已失效，请重新登录')
    } else {
      const data = error.response?.data
      const message = data
        ? Object.values(data)
            .flat()
            .join('；')
        : '加入购物车失败，请检查后端服务'

      ElMessage.error(message)
    }
  }
}


function goCart() {
  router.push('/cart')
}

function goOrders() {
  if (!localStorage.getItem('access_token')) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return
  }

  router.push('/orders')
}

function goProductManage() {
  router.push('/product-manage')
}

function goProductDetail(productId) {
  router.push(`/products/${productId}`)
}
onMounted(() => {
  loadProducts()
  loadCategories()
  loadCurrentUser()
})
</script>


<style scoped>
.category-filter {
  margin: 20px 0 12px;
  overflow-x: auto;
}
.category-filter :deep(.el-radio-group) {
  display: inline-flex;
  flex-wrap: nowrap;
}

.sort-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  color: #666065;
  font-size: 14px;
}

</style>
