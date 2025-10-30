<script setup lang="ts">
import { useRouter } from 'vue-router'
import { api } from '../api'
import { message } from 'ant-design-vue'

const router = useRouter()

const getPageTitle = () => {
  const path = router.currentRoute.value.path
  const titles: Record<string, string> = {
    '/': '仪表盘',
    '/products': '产品管理',
    '/import': '批量导入'
  }
  return titles[path] || '后台管理'
}

const handleLogout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('role')
  message.success('已退出登录')
  router.push('/login')
}
</script>

<template>
  <a-layout style="min-height: 100vh;">
    <a-layout-sider width="220" style="background: linear-gradient(180deg, #001529 0%, #002140 100%);">
      <div style="color:#fff;padding:20px;font-weight:600;font-size:18px;border-bottom:1px solid rgba(255,255,255,0.1);">
        <span style="font-size:24px;">🤖</span> Modellion
      </div>
      <a-menu theme="dark" mode="inline" :selectedKeys="[router.currentRoute.value.path]" @click="(e:any)=>router.push(e.key)">
        <a-menu-item key="/">
          <template #icon><span style="font-size:16px;">📊</span></template>
          仪表盘
        </a-menu-item>
        <a-menu-item key="/products">
          <template #icon><span style="font-size:16px;">📦</span></template>
          产品管理
        </a-menu-item>
        <a-menu-item key="/import">
          <template #icon><span style="font-size:16px;">📥</span></template>
          批量导入
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background:#fff;padding:0 24px;box-shadow:0 2px 8px rgba(0,0,0,0.06);display:flex;align-items:center;justify-content:space-between;">
        <h2 style="margin:0;font-size:20px;font-weight:500;">{{ getPageTitle() }}</h2>
        <a-button @click="handleLogout" danger>退出登录</a-button>
      </a-layout-header>
      <a-layout-content style="padding:24px;background:#f0f2f5;">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<style scoped>
</style>


