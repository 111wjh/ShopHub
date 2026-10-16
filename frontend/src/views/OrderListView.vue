<template>
  <div class="order-list-page">
    <div class="page-header">
      <h2>我的订单</h2>
      <div class="header-actions">
        <el-button
          :loading="loading"
          @click="loadOrders"
        >
          刷新订单
        </el-button>
      
        <el-button @click="router.push('/')">
        返回首页
        </el-button>
      </div>
    </div>
  
    <el-card class="order-card">
      <!-- 订单状态筛选 -->
      <div class="filter-bar">
        <el-radio-group v-model="selectedStatus">
          <el-radio-button label="全部" value="all" />
          <el-radio-button label="待支付" value="pending" />
          <el-radio-button label="已支付" value="paid" />
          <el-radio-button label="已发货" value="shipped" />
          <el-radio-button label="已完成" value="completed" />
          <el-radio-button label="已取消" value="cancelled" />
        </el-radio-group>
      </div>
      <div v-if="loading" class="loading">
        正在加载订单...
      </div>

      <el-empty
        v-else-if="filteredOrders.length === 0"
        :description="selectedStatus === 'all'
          ? '暂时没有订单'
          : '没有符合该状态的订单'"
      />

      <div v-else class="order-list">
        <div
          v-for="order in filteredOrders"
          :key="order.id"
          class="order-item"
        >
          <div class="order-info">
            <div class="order-top">
              <span class="order-number">
                订单编号：{{ order.order_number || order.id }}
              </span>

              <el-tag
                :type="statusType(order.status)"
              >
                {{ statusText(order.status) }}
              </el-tag>
            </div>

            <div class="order-time">
              下单时间：{{ formatDate(order.created_at) }}
            </div>

            <div class="order-bottom">
              <div class="order-amount">
                订单金额：
                <span>¥{{ formatPrice(order.total_amount) }}</span>
              </div>

              <el-button
                type="primary"
                plain
                @click="viewDetail(order.id)"
              >
                查看详情
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const router = useRouter()

const API_BASE_URL = 'http://localhost:8080/api'

const orders = ref([])
const loading = ref(false)
const selectedStatus = ref('all')
// 根据选择的状态筛选订单
const filteredOrders = computed(() => {
  if (selectedStatus.value === 'all') {
    return orders.value
  }

  return orders.value.filter(
    order => order.status === selectedStatus.value
  )
})
const statusMap = {
  pending: '待支付',
  paid: '已支付',
  shipped: '已发货',
  completed: '已完成',
  cancelled: '已取消',
}

function statusText(status) {
  return statusMap[status] || status || '未知'
}

function statusType(status) {
  const types = {
    pending: 'warning',
    paid: 'primary',
    shipped: 'success',
    completed: 'success',
    cancelled: 'info',
  }

  return types[status] || 'info'
}

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

async function loadOrders() {
  const config = getAuthConfig()
  if (!config) return

  loading.value = true

  try {
    const response = await axios.get(
      `${API_BASE_URL}/orders/`,
      config,
    )

    const data = response.data

    // 兼容普通数组和 DRF 分页返回格式
    orders.value = Array.isArray(data)
      ? data
      : Array.isArray(data.results)
        ? data.results
        : []
  } catch (error) {
    console.error('获取订单列表失败：', error)
    ElMessage.error(
      error.response?.data?.detail || '获取订单列表失败',
    )
  } finally {
    loading.value = false
  }
}

function viewDetail(orderId) {
  router.push(`/orders/${orderId}`)
}

onMounted(loadOrders)
</script>

<style scoped>
.order-list-page {
  min-height: 100vh;
  padding: 30px 20px;
  background: #f5f7fa;
}

.page-header {
  max-width: 1000px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.page-header h2 {
  margin: 0;
  color: #303133;
}

.order-card {
  max-width: 1000px;
  margin: 0 auto;
  border-radius: 12px;
}

.filter-bar {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #ebeef5;
  overflow-x: auto;
}

.filter-bar :deep(.el-radio-group) {
  display: inline-flex;
  flex-wrap: nowrap;
}

.loading {
  padding: 50px 0;
  text-align: center;
  color: #909399;
}

.order-item {
  padding: 20px 0;
  border-bottom: 1px solid #ebeef5;
}

.order-item:first-child {
  padding-top: 5px;
}

.order-item:last-child {
  border-bottom: none;
}

.order-top,
.order-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.order-number {
  font-weight: 600;
  color: #303133;
  overflow-wrap: anywhere;
}

.order-time {
  margin: 14px 0;
  color: #909399;
  font-size: 14px;
}

.order-amount {
  color: #606266;
}

.order-amount span {
  color: #e4393c;
  font-size: 20px;
  font-weight: bold;
}

@media (max-width: 600px) {
  .order-list-page {
    padding: 16px 10px;
  }

  .order-top,
  .order-bottom {
    align-items: flex-start;
  }

  .order-bottom {
    flex-direction: column;
  }
}
</style>