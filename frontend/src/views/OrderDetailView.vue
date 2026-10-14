
<template>
  <div class="order-page">
    <el-card class="order-card">
      <template #header>
        <div class="card-header">
          <h2>订单详情</h2>
          <el-button @click="router.push('/')">
            返回首页
          </el-button>
        </div>
      </template>

      <div v-if="loading" class="loading">
        正在加载订单...
      </div>

      <el-empty
        v-else-if="!order"
        description="暂时无法获取订单信息"
      />

      <template v-else>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="订单编号">
            {{ order.order_number || order.id }}
          </el-descriptions-item>

          <el-descriptions-item label="订单状态">
            <el-tag>{{ statusText }}</el-tag>
          </el-descriptions-item>

          <el-descriptions-item label="创建时间">
            {{ formatDate(order.created_at) }}
          </el-descriptions-item>

          <el-descriptions-item label="订单总金额">
            <span class="total-price">
              ¥{{ formatPrice(order.total_amount) }}
            </span>
          </el-descriptions-item>
        </el-descriptions>

        <h3>商品明细</h3>

        <el-table
          v-if="order.items && order.items.length"
          :data="order.items"
          stripe
          style="width: 100%"
        >
          <el-table-column
            prop="product_name"
            label="商品名称"
            min-width="160"
          />

          <el-table-column label="单价" width="120">
            <template #default="{ row }">
              ¥{{ formatPrice(row.price) }}
            </template>
          </el-table-column>

          <el-table-column
            prop="quantity"
            label="数量"
            width="100"
          />

          <el-table-column label="小计" width="140">
            <template #default="{ row }">
              ¥{{ formatPrice(row.price * row.quantity) }}
            </template>
          </el-table-column>
        </el-table>

        <el-empty
          v-else
          description="暂无商品明细"
        />

        <div class="actions">
          <el-button @click="router.push('/cart')">
            返回购物车
          </el-button>

          <el-button
            v-if="order.status === 'pending'"
            type="primary"
            :loading="paying"
            @click="payOrder"
          >
            模拟支付
          </el-button>
          <el-button
            v-if="order.status === 'pending'"
            type="danger"
            plain
            :loading="cancelling"
            @click="cancelOrder"
          >
              取消订单
          </el-button>
          <el-button
            v-if="order.status === 'shipped'"
            type="success"
            :loading="completing"
            @click="completeOrder"
          >
            确认收货
          </el-button>
          <el-button
            v-if="isStaff && order.status === 'paid'"
            type="primary"
            :loading="shipping"
            @click="shipOrder"
          >
            管理员发货
          </el-button>
        </div>
      </template>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()

const API_BASE_URL = 'http://127.0.0.1:8000/api'

const order = ref(null)
const loading = ref(false)
const paying = ref(false)
const isStaff = ref(false)
const cancelling = ref(false)
const completing = ref(false)
const shipping = ref(false)
const statusMap = {
  pending: '待支付',
  paid: '已支付',
  shipped: '已发货',
  completed: '已完成',
  cancelled: '已取消',
}

const statusText = computed(() => {
  return statusMap[order.value?.status] || order.value?.status || '未知'
})

function formatPrice(value) {
  return Number(value || 0).toFixed(2)
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('zh-CN')
}

function getAuthConfig() {
  const token = localStorage.getItem('access_token')

  if (!token) {
    ElMessage.warning('请先登录')
    router.push('/login')
    return null
  }

  return {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  }
}

async function loadOrder() {
  const config = getAuthConfig()
  if (!config) return

  loading.value = true

  try {
    const response = await axios.get(
      `${API_BASE_URL}/orders/${route.params.id}/`,
      config,
    )

    order.value = response.data
    // 获取当前登录用户的管理员身份
    try {
      const userResponse = await axios.get(
        `${API_BASE_URL}/users/me/`,
        config,
      )

      isStaff.value = userResponse.data.is_staff === true
    } catch (error) {
      console.error('获取用户身份失败：', error)
      isStaff.value = false
    }
  } catch (error) {
    console.error('获取订单详情失败：', error)
    ElMessage.error(
      error.response?.data?.detail || '获取订单详情失败',
    )
  } finally {
    loading.value = false
  }
}

async function payOrder() {
  const config = getAuthConfig()
  if (!config) return

  paying.value = true

  try {
    await axios.post(
      `${API_BASE_URL}/orders/${route.params.id}/pay/`,
      {},
      config,
    )

    ElMessage.success('支付成功')
    await loadOrder()
  } catch (error) {
    console.error('订单支付失败：', error)

    const data = error.response?.data
    const message = data
      ? Object.values(data).flat().join('；')
      : '支付失败，请稍后重试'

    ElMessage.error(message)
  } finally {
    paying.value = false
  }
}

async function cancelOrder() {
  const config = getAuthConfig()
  if (!config) return

  try {
    await ElMessageBox.confirm(
      '确定要取消这笔订单吗？取消后无法恢复。',
      '取消订单',
      {
        confirmButtonText: '确定取消',
        cancelButtonText: '暂不取消',
        type: 'warning',
      },
    )
  } catch {
    return
  }

  cancelling.value = true

  try {
    await axios.post(
      `${API_BASE_URL}/orders/${route.params.id}/cancel/`,
      {},
      config,
    )

    ElMessage.success('订单已取消')
    await loadOrder()
  } catch (error) {
    console.error('取消订单失败：', error)

    const data = error.response?.data
    const message = data
      ? Object.values(data).flat().join('；')
      : '取消订单失败，请稍后重试'

    ElMessage.error(message)
  } finally {
    cancelling.value = false
  }
}


async function completeOrder() {
  const config = getAuthConfig()
  if (!config) return

  try {
    await ElMessageBox.confirm(
      '确认已经收到商品了吗？',
      '确认收货',
      {
        confirmButtonText: '确认收货',
        cancelButtonText: '再检查一下',
        type: 'success',
      },
    )
  } catch {
    return
  }

  completing.value = true

  try {
    await axios.post(
      `${API_BASE_URL}/orders/${route.params.id}/complete/`,
      {},
      config,
    )

    ElMessage.success('确认收货成功')
    await loadOrder()
  } catch (error) {
    console.error('确认收货失败：', error)

    const data = error.response?.data
    const message = data
      ? Object.values(data).flat().join('；')
      : '确认收货失败，请稍后重试'

    ElMessage.error(message)
  } finally {
    completing.value = false
  }
}


async function shipOrder() {
  const config = getAuthConfig()
  if (!config) return

  try {
    await ElMessageBox.confirm(
      '确定要发货吗？',
      '管理员发货',
      {
        confirmButtonText: '确认发货',
        cancelButtonText: '暂不发货',
        type: 'warning',
      },
    )
  } catch {
    return
  }

  shipping.value = true

  try {
    await axios.post(
      `${API_BASE_URL}/orders/${route.params.id}/ship/`,
      {},
      config,
    )

    ElMessage.success('订单发货成功')
    await loadOrder()
  } catch (error) {
    console.error('订单发货失败：', error)

    const data = error.response?.data
    const message = data
      ? Object.values(data).flat().join('；')
      : '订单发货失败，请稍后重试'

    ElMessage.error(message)
  } finally {
    shipping.value = false
  }
}


onMounted(loadOrder)
</script>

<style scoped>
.order-page {
  min-height: 100vh;
  padding: 30px 20px;
  background: #f5f7fa;
}

.order-card {
  max-width: 1000px;
  margin: 0 auto;
  border-radius: 12px;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.card-header h2 {
  margin: 0;
  font-size: 22px;
}

.loading {
  padding: 50px 0;
  text-align: center;
  color: #909399;
}

.total-price {
  color: #e4393c;
  font-size: 22px;
  font-weight: bold;
}

h3 {
  margin: 28px 0 16px;
}

.actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}
</style>
