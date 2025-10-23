<script setup lang="ts">
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { api } from '../api'
import { setRole, setToken } from '../utils/auth'

const router = useRouter()
const form = reactive({ username: '', password: '' })

async function onFinish() {
  try {
    const res = await api.login(form.username, form.password)
    setToken(res.access_token)
    const me = await api.me()
    setRole(me.role)
    message.success('登录成功')
    router.push('/')
  } catch (e: any) {
    message.error(e.message || '登录失败')
  }
}
</script>

<template>
  <div style="display:flex;height:100vh;align-items:center;justify-content:center;">
    <a-card title="登录" style="width:360px;">
      <a-form layout="vertical" :model="form" @finish="onFinish">
        <a-form-item label="用户名" name="username" :rules="[{ required: true }]">
          <a-input v-model:value="form.username" />
        </a-form-item>
        <a-form-item label="密码" name="password" :rules="[{ required: true }]">
          <a-input-password v-model:value="form.password" />
        </a-form-item>
        <a-button type="primary" html-type="submit" block>登录</a-button>
      </a-form>
    </a-card>
  </div>
  
</template>

<style scoped>
</style>


