
import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../views/HomeView.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('../views/RegisterView.vue'),
  },
  {
  path: '/login',
  name: 'login',
  component: () => import('../views/LoginView.vue'),
  },
  
  {
  path: '/cart',
  name: 'cart',
  component: () => import('../views/CartView.vue'),
  },
  {
  path: '/orders/:id',
  name: 'order-detail',
  component: () => import('../views/OrderDetailView.vue'),
  },
  {
  path: '/orders',
  name: 'order-list',
  component: () => import('../views/OrderListView.vue'),
  },
  {
  path: '/product-manage',
  name: 'ProductManage',
  component: () => import('../views/ProductManageView.vue'),
 },
 {
  path: '/products/:id',
  name: 'product-detail',
  component: () => import('../views/ProductDetailView.vue'),
},
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
