import { createRouter, createWebHistory } from 'vue-router'
import Layout from './pages/Layout.vue'
import Login from './pages/Login.vue'
import Dashboard from './pages/Dashboard.vue'
import Products from './pages/Products.vue'
import ProductEdit from './pages/ProductEdit.vue'
import Images from './pages/Images.vue'
import ImportPage from './pages/Import.vue'
import ProductDetail from './pages/ProductDetail.vue'
import { api } from './api'

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', name: 'login', component: Login },
    {
      path: '/',
      component: Layout,
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: Dashboard },
        { path: 'products', name: 'products', component: Products },
        { path: 'products/:id', name: 'product-edit', component: ProductEdit },
        { path: 'products/:id/detail', name: 'product-detail', component: ProductDetail },
        { path: 'images/:productId', name: 'images', component: Images },
        { path: 'import', name: 'import', component: ImportPage },
      ],
    },
  ],
})

// 路由守卫：验证token有效性
router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  
  // 如果目标路径是登录页，直接放行
  if (to.path === '/login') {
    next()
    return
  }
  
  // 如果没有token，跳转到登录页
  if (!token) {
    next('/login')
    return
  }
  
  // 如果需要认证（默认Layout下所有页面都需要）
  if (to.matched.some(record => record.meta.requiresAuth)) {
    try {
      // 调用 /api/auth/me 验证token是否有效
      await api.me()
      next()
    } catch (error) {
      // token无效或过期，清除并跳转到登录页
      console.warn('Token验证失败，跳转到登录页')
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      next('/login')
    }
  } else {
    next()
  }
})


