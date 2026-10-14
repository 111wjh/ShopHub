
<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>登录 ShopHub</h2>
      <p class="subtitle">欢迎回来，继续购物</p>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            autocomplete="current-password"
          />
        </el-form-item>

        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          class="submit-button"
        >
          登录
        </el-button>
      </el-form>

      <div class="register-link">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>

      <div class="back-home">
        <router-link to="/">返回首页</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_BASE_URL = 'http://127.0.0.1:8000/api'

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
  ],
}

const handleLogin = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
  } catch {
    return
  }

  loading.value = true

  try {
    const response = await axios.post(
      `${API_BASE_URL}/users/login/`,
      {
        username: form.username,
        password: form.password,
      },
    )

    // 保存 JWT 令牌，后续请求需要使用
    localStorage.setItem('access_token', response.data.access)
    localStorage.setItem('refresh_token', response.data.refresh)

    ElMessage.success('登录成功')

    // 返回首页
    window.location.href = '/'
  } catch (error) {
    const data = error.response?.data
    const message = data?.detail || '登录失败，请检查用户名和密码'

    ElMessage.error(message)
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 24px;
  background: #f5f7fa;
}

.login-card {
  width: 100%;
  max-width: 440px;
  border-radius: 12px;
}

h2 {
  margin: 0;
  text-align: center;
  color: #303133;
}

.subtitle {
  margin: 10px 0 28px;
  text-align: center;
  color: #909399;
}

.submit-button {
  width: 100%;
  margin-top: 8px;
}

.register-link,
.back-home {
  margin-top: 20px;
  text-align: center;
  color: #606266;
}

.back-home {
  margin-top: 12px;
}

a {
  color: #409eff;
  text-decoration: none;
}
</style>
