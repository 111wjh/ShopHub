<template>
  <div class="product-manage-page">
    <header class="page-header">
      <h2>商品管理</h2>

      <div class="header-actions">
        <el-button @click="goHome">返回首页</el-button>
        <el-button type="success" @click="openCreateDialog">
          新增商品
        </el-button>
        <el-button type="primary" @click="loadProducts"> 刷新商品 </el-button>
      </div>
    </header>

    <el-card>
      <!-- 商品搜索和状态筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchKeyword"
          placeholder="请输入商品名称搜索"
          clearable
          style="width: 260px"
        />

        <el-select
          v-model="statusFilter"
          placeholder="选择商品状态"
          style="width: 160px"
        >
          <el-option label="全部商品" value="all" />
          <el-option label="已上架" value="active" />
          <el-option label="已下架" value="inactive" />
        </el-select>
      </div>

      <div v-if="loading" class="loading">正在加载商品...</div>

      <el-alert
        v-else-if="errorMessage"
        :title="errorMessage"
        type="error"
        show-icon
        :closable="false"
      />

      <el-empty v-else-if="products.length === 0" description="暂无商品" />

      <el-table v-else :data="paginatedProducts" stripe style="width: 100%">
        <el-table-column prop="id" label="商品 ID" width="100" />

        <el-table-column prop="name" label="商品名称" min-width="180" />

        <el-table-column label="商品价格" width="160">
          <template #default="{ row }"> ¥{{ row.price }} </template>
        </el-table-column>

        <el-table-column prop="stock" label="库存" width="120" />

        <el-table-column label="商品状态" width="120">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'">
              {{ row.is_active ? "已上架" : "已下架" }}
            </el-tag>
          </template>
        </el-table-column>

        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" link @click="openEditDialog(row)">
              编辑
            </el-button>

            <el-button type="danger" link @click="deleteProduct(row)">
              删除
            </el-button>

            <el-button
              :type="row.is_active ? 'warning' : 'success'"
              link
              @click="toggleProductStatus(row)"
            >
              {{ row.is_active ? "下架" : "上架" }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <!-- 商品分页 -->
      <div class="pagination-bar">
        <el-pagination
          :current-page="currentPage"
          :page-size="pageSize"
          :page-sizes="[5, 10, 20, 50]"
          :total="filteredProducts.length"
          layout="total, sizes, prev, pager, next, jumper"
          @current-change="currentPage = $event"
          @size-change="pageSize = $event"
        />
      </div>
    </el-card>

    <el-dialog
      v-model="createDialogVisible"
      @closed="handleCreateImageRemove"
      title="新增商品"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="createForm.name" placeholder="请输入商品名称" />
        </el-form-item>

        <el-form-item label="商品分类" prop="category_id">
          <el-select
            v-model="createForm.category_id"
            placeholder="请选择商品分类"
            style="width: 100%"
          >
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入商品描述"
          />
        </el-form-item>

        <el-form-item label="商品价格" prop="price">
          <el-input-number
            v-model="createForm.price"
            :min="0.01"
            :precision="2"
            :step="10"
          />
        </el-form-item>

        <el-form-item label="商品库存" prop="stock">
          <el-input-number v-model="createForm.stock" :min="0" :precision="0" />
        </el-form-item>

        <el-form-item label="商品图片">
          <div class="image-upload-row">
            <!-- 新图片预览 -->
            <div v-if="createImagePreview" class="current-image">
              <img :src="createImagePreview" alt="新商品图片预览" />
              <div class="image-caption">图片预览</div>
            </div>

            <!-- 选择图片 -->
            <div class="new-image">
              <el-upload
                :auto-upload="false"
                :limit="1"
                accept="image/jpeg,image/png,image/webp"
                list-type="picture-card"
                :on-change="handleCreateImageChange"
                :on-remove="handleCreateImageRemove"
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
              <div class="image-caption">选择商品图片</div>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="是否上架" prop="is_active">
          <el-switch v-model="createForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false"> 取消 </el-button>
        <el-button type="primary" :loading="creating" @click="createProduct">
          保存商品
        </el-button>
      </template>
    </el-dialog>

    <!-- 编辑商品弹窗 -->
    <el-dialog
      v-model="editDialogVisible"
      @closed="handleEditImageRemove"
      title="编辑商品"
      width="600px"
      destroy-on-close
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="100px"
      >
        <el-form-item label="商品名称" prop="name">
          <el-input v-model="editForm.name" placeholder="请输入商品名称" />
        </el-form-item>

        <el-form-item label="商品分类" prop="category_id">
          <el-select
            v-model="editForm.category_id"
            placeholder="请选择商品分类"
            style="width: 100%"
          >
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="商品描述" prop="description">
          <el-input
            v-model="editForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入商品描述"
          />
        </el-form-item>

        <el-form-item label="商品价格" prop="price">
          <el-input-number
            v-model="editForm.price"
            :min="0.01"
            :precision="2"
            :step="10"
          />
        </el-form-item>

        <el-form-item label="商品库存" prop="stock">
          <el-input-number v-model="editForm.stock" :min="0" :precision="0" />
        </el-form-item>

        <!-- 编辑商品图片 -->

        <el-form-item label="商品图片">
          <div class="image-upload-row">
            <!-- 优先显示新图片预览，否则显示已保存的原图片 -->
            <div v-if="editImagePreview || editImageUrl" class="current-image">
              <img
                :src="editImagePreview || getImageUrl(editImageUrl)"
                alt="商品图片预览"
              />
              <div class="image-caption">
                {{ editImagePreview ? "新图片预览" : "当前商品图片" }}
              </div>
            </div>

            <!-- 选择新图片 -->
            <div class="new-image">
              <el-upload
                :auto-upload="false"
                :limit="1"
                accept="image/jpeg,image/png,image/webp"
                list-type="picture-card"
                :on-change="handleEditImageChange"
                :on-remove="handleEditImageRemove"
              >
                <el-icon><Plus /></el-icon>
              </el-upload>
              <div class="image-caption">更换商品图片</div>
            </div>
          </div>
        </el-form-item>

        <el-form-item label="是否上架" prop="is_active">
          <el-switch v-model="editForm.is_active" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="editDialogVisible = false"> 取消 </el-button>
        <el-button type="primary" :loading="editing" @click="updateProduct">
          保存修改
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from "vue";
import { useRouter } from "vue-router";
import axios, { API_BASE_URL, getImageUrl, getAllPages } from "../services/api";
import { ElMessage, ElMessageBox } from "element-plus";
import { Plus } from "@element-plus/icons-vue";
const router = useRouter();

const products = ref([]);
const loading = ref(false);
const errorMessage = ref("");
// 商品名称搜索关键词
const searchKeyword = ref("");

// 商品上架状态筛选
const statusFilter = ref("all");

// 根据搜索关键词和商品状态筛选商品
const filteredProducts = computed(() => {
  return products.value.filter((product) => {
    // 商品名称搜索
    const matchesKeyword = product.name
      .toLowerCase()
      .includes(searchKeyword.value.trim().toLowerCase());

    // 商品状态筛选
    const matchesStatus =
      statusFilter.value === "all" ||
      (statusFilter.value === "active" && product.is_active) ||
      (statusFilter.value === "inactive" && !product.is_active);

    return matchesKeyword && matchesStatus;
  });
});

// 当前页码
const currentPage = ref(1);

// 搜索关键词或状态改变时，回到第一页
watch([searchKeyword, statusFilter], () => {
  currentPage.value = 1;
});
// 每页显示的商品数量
const pageSize = ref(5);
watch(pageSize, () => {
  currentPage.value = 1;
});
watch(
  () => filteredProducts.value.length,
  (length) => {
    currentPage.value = Math.max(
      1,
      Math.min(currentPage.value, Math.ceil(length / pageSize.value)),
    );
  },
);

// 当前页需要显示的商品
const paginatedProducts = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;

  return filteredProducts.value.slice(start, end);
});

// 新增商品弹窗状态
const createDialogVisible = ref(false);
const creating = ref(false);
const createFormRef = ref(null);

// 商品分类列表
const categories = ref([]);

// 新增商品表单
const createForm = ref({
  name: "",
  category_id: null,
  description: "",
  price: 0.01,
  stock: 0,
  is_active: true,
});

// 新增商品时选择的图片文件
const createImageFile = ref(null);
const createImagePreview = ref("");
// 表单校验规则
const createRules = {
  name: [
    { required: true, message: "请输入商品名称", trigger: "blur" },
    { max: 200, message: "商品名称不能超过 200 个字符", trigger: "blur" },
  ],
  category_id: [
    { required: true, message: "请选择商品分类", trigger: "change" },
  ],
  price: [{ required: true, message: "请输入商品价格", trigger: "change" }],
  stock: [{ required: true, message: "请输入商品库存", trigger: "change" }],
};

// 编辑商品弹窗状态
const editDialogVisible = ref(false);
const editing = ref(false);
const editFormRef = ref(null);

// 编辑商品表单
const editForm = ref({
  id: null,
  name: "",
  category_id: null,
  description: "",
  price: 0.01,
  stock: 0,
  is_active: true,
});

// 编辑商品时新选择的图片文件
const editImageFile = ref(null);

// 当前商品已经保存的图片地址
const editImageUrl = ref("");

const editImagePreview = ref("");
// 编辑表单校验规则
const editRules = {
  name: [
    { required: true, message: "请输入商品名称", trigger: "blur" },
    { max: 200, message: "商品名称不能超过 200 个字符", trigger: "blur" },
  ],
  category_id: [
    { required: true, message: "请选择商品分类", trigger: "change" },
  ],
  price: [{ required: true, message: "请输入商品价格", trigger: "change" }],
  stock: [{ required: true, message: "请输入商品库存", trigger: "change" }],
};

function goHome() {
  router.push("/");
}

// 打开新增商品弹窗，并加载商品分类
async function openCreateDialog() {
  handleCreateImageRemove();
  createForm.value = {
    name: "",
    category_id: null,
    description: "",
    price: 0.01,
    stock: 0,
    is_active: true,
  };

  createDialogVisible.value = true;

  try {
    const response = await axios.get(`${API_BASE_URL}/products/categories/`);

    categories.value = Array.isArray(response.data)
      ? response.data
      : response.data.results || [];

    if (categories.value.length === 0) {
      ElMessage.warning("当前没有商品分类，请先创建商品分类");
    }
  } catch (error) {
    console.error("获取商品分类失败：", error);
    ElMessage.error("获取商品分类失败，请检查后端服务");
  }
}

// 将商品图片路径转换成浏览器可以访问的完整 URL

// 打开编辑商品弹窗，并填入商品现有信息
async function openEditDialog(row) {
  handleEditImageRemove();
  // 加载分类，确保下拉框有可选项
  try {
    const response = await axios.get(`${API_BASE_URL}/products/categories/`);

    categories.value = Array.isArray(response.data)
      ? response.data
      : response.data.results || [];
  } catch (error) {
    console.error("获取商品分类失败：", error);
    ElMessage.error("获取商品分类失败");
    return;
  }

  // 将当前商品的数据填入编辑表单
  editForm.value = {
    id: row.id,
    name: row.name,
    category_id: row.category?.id ?? row.category_id ?? null,
    description: row.description || "",
    price: Number(row.price),
    stock: row.stock,
    is_active: row.is_active,
  };
  // 记录商品原来的图片地址
  editImageUrl.value = row.image || "";
  editImageFile.value = null;
  editDialogVisible.value = true;
}

// 提交商品修改
async function updateProduct() {
  if (!editFormRef.value) return;

  // 校验表单

  try {
    await editFormRef.value.validate();
  } catch {
    return;
  }

  const token = localStorage.getItem("access_token");

  if (!token) {
    ElMessage.warning("请先登录管理员账号");
    router.push("/login");
    return;
  }

  editing.value = true;

  try {
    const productId = editForm.value.id;

    // 使用 FormData 提交商品信息
    const formData = new FormData();

    const payload = {
      name: editForm.value.name,
      category_id: editForm.value.category_id,
      description: editForm.value.description,
      price: editForm.value.price,
      stock: editForm.value.stock,
      is_active: editForm.value.is_active,
    };

    Object.entries(payload).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formData.append(key, value);
      }
    });

    // 只有选择了新图片时，才上传图片
    if (editImageFile.value) {
      formData.append("image", editImageFile.value);
    }

    await axios.put(`${API_BASE_URL}/products/${productId}/update/`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    ElMessage.success("商品修改成功");
    editDialogVisible.value = false;
    editImageFile.value = null;

    // 重新加载商品列表
    await loadProducts();
  } catch (error) {
    console.error("修改商品失败：", error);

    const data = error.response?.data;
    const message = data
      ? Object.entries(data)
          .map(([key, value]) => {
            const detail = Array.isArray(value)
              ? value.join("、")
              : typeof value === "object"
                ? JSON.stringify(value)
                : value;

            return `${key}: ${detail}`;
          })
          .join("；")
      : "修改商品失败，请检查后端服务";

    ElMessage.error(message);
  } finally {
    editing.value = false;
  }
}

// 删除商品
async function deleteProduct(row) {
  try {
    // 删除前让管理员确认
    await ElMessageBox.confirm(
      `确定要删除商品「${row.name}」吗？此操作不可撤销。`,
      "删除确认",
      {
        confirmButtonText: "确定删除",
        cancelButtonText: "取消",
        type: "warning",
      },
    );
  } catch {
    // 用户点击取消，不执行删除
    return;
  }

  const token = localStorage.getItem("access_token");

  if (!token) {
    ElMessage.warning("请先登录管理员账号");
    router.push("/login");
    return;
  }

  try {
    await axios.delete(`${API_BASE_URL}/products/${row.id}/delete/`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    ElMessage.success("商品删除成功");
    await loadProducts();
  } catch (error) {
    console.error("删除商品失败：", error);

    const data = error.response?.data;
    const message = data
      ? JSON.stringify(data)
      : "删除商品失败，请检查后端服务";

    ElMessage.error(message);
  }
}

// 切换商品上架状态
async function toggleProductStatus(row) {
  const token = localStorage.getItem("access_token");

  if (!token) {
    ElMessage.warning("请先登录管理员账号");
    router.push("/login");
    return;
  }

  const newStatus = !row.is_active;

  try {
    await axios.patch(
      `${API_BASE_URL}/products/${row.id}/update/`,
      {
        is_active: newStatus,
      },
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      },
    );

    ElMessage.success(newStatus ? "商品上架成功" : "商品下架成功");

    await loadProducts();
  } catch (error) {
    console.error("修改商品状态失败：", error);

    const data = error.response?.data;
    const message = data
      ? JSON.stringify(data)
      : "修改商品状态失败，请检查后端服务";

    ElMessage.error(message);
  }
}

// 记录选择的图片文件

function handleCreateImageChange(uploadFile) {
  const file = uploadFile.raw;

  if (!file) return;

  // 检查图片格式
  const allowedTypes = ["image/jpeg", "image/png", "image/webp"];

  if (!allowedTypes.includes(file.type)) {
    ElMessage.error("只允许上传 JPG、PNG、WEBP 格式的图片");
    return;
  }

  // 检查图片大小
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error("图片大小不能超过 5 MB");
    return;
  }

  // 保存待上传文件
  createImageFile.value = file;

  // 生成本地预览地址
  createImagePreview.value = URL.createObjectURL(file);
}

// 移除图片时清空文件

function handleCreateImageRemove() {
  createImageFile.value = null;

  // 释放临时预览地址
  if (createImagePreview.value) {
    URL.revokeObjectURL(createImagePreview.value);
    createImagePreview.value = "";
  }
}

// 记录编辑商品时选择的新图片

function handleEditImageChange(uploadFile) {
  const file = uploadFile.raw;

  if (!file) return;

  // 检查图片格式
  const allowedTypes = ["image/jpeg", "image/png", "image/webp"];

  if (!allowedTypes.includes(file.type)) {
    ElMessage.error("只允许上传 JPG、PNG、WEBP 格式的图片");
    return;
  }

  // 检查图片大小
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error("图片大小不能超过 5 MB");
    return;
  }

  // 保存待上传文件
  editImageFile.value = file;

  // 生成新图片的本地预览地址
  if (editImagePreview.value) {
    URL.revokeObjectURL(editImagePreview.value);
  }

  editImagePreview.value = URL.createObjectURL(file);
}

// 移除编辑时选择的图片

function handleEditImageRemove() {
  // 清除准备上传的新图片
  editImageFile.value = null;

  // 释放新图片的临时预览地址
  if (editImagePreview.value) {
    URL.revokeObjectURL(editImagePreview.value);
    editImagePreview.value = "";
  }
}

// 提交新增商品
async function createProduct() {
  if (!createFormRef.value) return;

  try {
    await createFormRef.value.validate();
  } catch {
    return;
  }

  const token = localStorage.getItem("access_token");

  if (!token) {
    ElMessage.warning("请先登录管理员账号");
    router.push("/login");
    return;
  }

  creating.value = true;

  try {
    // 使用 FormData 发送商品信息和图片
    const formData = new FormData();

    Object.entries(createForm.value).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        formData.append(key, value);
      }
    });

    // 如果选择了图片，就一并上传
    if (createImageFile.value) {
      formData.append("image", createImageFile.value);
    }

    await axios.post(`${API_BASE_URL}/products/create/`, formData, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    ElMessage.success("商品新增成功");
    createDialogVisible.value = false;
    createImageFile.value = null;

    await loadProducts();
  } catch (error) {
    console.error("新增商品失败：", error);

    const data = error.response?.data;
    const message = data
      ? Object.entries(data)
          .map(([key, value]) => {
            const detail = Array.isArray(value)
              ? value.join("、")
              : typeof value === "object"
                ? JSON.stringify(value)
                : value;

            return `${key}: ${detail}`;
          })
          .join("；")
      : "新增商品失败，请检查后端服务";

    ElMessage.error(message);
  } finally {
    creating.value = false;
  }
}

async function loadProducts() {
  loading.value = true;
  errorMessage.value = "";

  try {
    const token = localStorage.getItem("access_token");

    products.value = await getAllPages(`${API_BASE_URL}/products/`, {
      params: { manage: "true" },
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    });
  } catch (error) {
    console.error("获取商品列表失败：", error);

    errorMessage.value =
      error.response?.data?.detail || "获取商品列表失败，请检查后端服务";

    ElMessage.error(errorMessage.value);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadProducts();
});
onUnmounted(() => {
  handleCreateImageRemove();
  handleEditImageRemove();
});
</script>
