<template>
  <div class="register-page">
    <el-card class="register-card">
      <h2>创建 ShopHub 账号</h2>
      <p class="subtitle">注册后即可开始购物</p>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        label-position="top"
        @submit.prevent="handleRegister"
      >
        <el-form-item label="用户名" prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item label="邮箱" prop="email">
          <el-input
            v-model="form.email"
            type="email"
            placeholder="请输入邮箱"
            autocomplete="email"
          />
        </el-form-item>

        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="至少输入 6 位密码"
            show-password
            autocomplete="new-password"
          />
        </el-form-item>

        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            type="password"
            placeholder="请再次输入密码"
            show-password
            autocomplete="new-password"
          />
        </el-form-item>

        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          class="submit-button"
        >
          注册
        </el-button>
      </el-form>

      <div class="login-link">
        已有账号？
        <router-link to="/login">立即登录</router-link>
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
import { useRouter } from "vue-router";
const router = useRouter();

const formRef = ref(null);
const loading = ref(false);

const form = reactive({
  username: "",
  email: "",
  password: "",
  confirmPassword: "",
});

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error("两次输入的密码不一致"));
  } else {
    callback();
  }
};

const rules = {
  username: [{ required: true, message: "请输入用户名", trigger: "blur" }],
  email: [
    { required: true, message: "请输入邮箱", trigger: "blur" },
    { type: "email", message: "请输入有效的邮箱地址", trigger: "blur" },
  ],
  password: [
    { required: true, message: "请输入密码", trigger: "blur" },
    { min: 6, message: "密码至少需要 6 位", trigger: "blur" },
  ],
  confirmPassword: [
    { required: true, message: "请确认密码", trigger: "blur" },
    { validator: validateConfirmPassword, trigger: "blur" },
  ],
};

const handleRegister = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
  } catch {
    return;
  }

  loading.value = true;

  try {
    await axios.post(`${API_BASE_URL}/users/register/`, {
      username: form.username,
      email: form.email,
      password: form.password,
    });

    ElMessage.success("注册成功，请登录");

    form.username = "";
    form.email = "";
    form.password = "";
    form.confirmPassword = "";
    router.push("/login");
  } catch (error) {
    const data = error.response?.data;
    const message = data
      ? Object.entries(data)
          .map(
            ([field, messages]) =>
              `${field}: ${Array.isArray(messages) ? messages.join("、") : messages}`,
          )
          .join("；")
      : "无法连接服务器，请检查 Django 后端是否启动";

    ElMessage.error(message);
  } finally {
    loading.value = false;
  }
};
</script>
