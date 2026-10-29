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
import { reactive, ref } from "vue";
import axios, { API_BASE_URL } from "../services/api";
import { ElMessage } from "element-plus";
import { useRoute, useRouter } from "vue-router";
const route = useRoute();
const router = useRouter();

const formRef = ref(null);
const loading = ref(false);

const form = reactive({
  username: "",
  password: "",
});

const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  password: [{ required: true, message: "请输入密码", trigger: "blur" }],
};

const handleLogin = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
  } catch {
    return;
  }

  loading.value = true;

  try {
    const response = await axios.post(`${API_BASE_URL}/users/login/`, {
      username: form.username,
      password: form.password,
    });

    // 保存 JWT 令牌，后续请求需要使用
    localStorage.setItem("access_token", response.data.access);
    localStorage.setItem("refresh_token", response.data.refresh);

    ElMessage.success("登录成功");

    // 返回首页
    window.dispatchEvent(new Event("auth-changed"));
    const target = String(route.query.redirect || "/");
    await router.replace(
      target.startsWith("/") && !target.startsWith("//") ? target : "/",
    );
  } catch (error) {
    const data = error.response?.data;
    const message = data?.detail || "登录失败，请检查用户名和密码";

    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
};
</script>
