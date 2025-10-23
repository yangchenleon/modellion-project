<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { api } from '../api'
import { message } from 'ant-design-vue'

const route = useRoute()
const router = useRouter()
const id = route.params.id as string | undefined
const isCreate = !id || id === '0'
const loading = ref(false)
const form = ref<any>({ product_tag: '', series: '' })

onMounted(async () => {
  if (!isCreate) {
    const r = await api.getProduct(Number(id))
    form.value = r as any
  }
})

async function onSubmit() {
  try {
    loading.value = true
    if (isCreate) {
      await api.createProduct(form.value)
      message.success('已创建')
    } else {
      await api.updateProduct(Number(id), form.value)
      message.success('已保存')
    }
    router.push('/products')
  } catch (e: any) {
    if (e?.message) message.error(e.message)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <a-card :title="isCreate ? '新建产品' : '编辑产品'">
    <a-form layout="vertical">
      <a-form-item label="名称">
        <a-input v-model:value="form.product_name" />
      </a-form-item>
      <a-form-item label="价格">
        <a-input v-model:value="form.price" placeholder="例如 2,200円" />
      </a-form-item>
      <a-form-item label="发布日期">
        <a-input v-model:value="form.release_date" placeholder="例如 2025-01" />
      </a-form-item>
      <a-form-item label="URL" :rules="[{ required: true }]">
        <a-input v-model:value="form.url" />
      </a-form-item>
      <a-form-item label="标签">
        <a-input v-model:value="form.product_tag" />
      </a-form-item>
      <a-form-item label="系列">
        <a-input v-model:value="form.series" />
      </a-form-item>
      <a-form-item label="正文(HTML)">
        <a-textarea v-model:value="form.article_content" :rows="6" />
      </a-form-item>
      <a-space>
        <a-button @click="()=>router.back()">返回</a-button>
        <a-button type="primary" :loading="loading" @click="onSubmit">保存</a-button>
      </a-space>
    </a-form>
  </a-card>
</template>

<style scoped>
</style>


