<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()
</script>

<template>
  <a-layout style="min-height: 100vh;">
    <a-layout-sider>
      <div style="color:#fff;padding:16px;font-weight:600;">后台管理</div>
      <a-menu theme="dark" mode="inline" @click="(e:any)=>router.push(e.key)">
        <a-menu-item key="/">仪表盘</a-menu-item>
        <a-menu-item key="/products">产品</a-menu-item>
        <a-menu-item key="/import">导入</a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header style="background:#fff" />
      <a-layout-content style="padding:16px;">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<style scoped>
</style>


