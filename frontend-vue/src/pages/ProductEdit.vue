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
  <a-card :bordered="false" style="box-shadow: 0 2px 8px rgba(0,0,0,0.09);">
    <template #title>
      <span style="font-size:18px;font-weight:500;">{{ isCreate ? '➕ 新建产品' : '✏️ 编辑产品' }}</span>
    </template>
    
    <a-form layout="vertical" :label-col="{ span: 6 }">
      <a-row :gutter="24">
        <a-col :span="12">
          <a-form-item label="名称（日文）">
            <a-input v-model:value="form.product_name" placeholder="日文产品名称" />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="名称（中文）">
            <a-input v-model:value="form.product_name_cn" placeholder="自动翻译或手动输入" />
          </a-form-item>
        </a-col>
      </a-row>
      
      <a-row :gutter="24">
        <a-col :span="12">
          <a-form-item label="价格">
            <a-input v-model:value="form.price" placeholder="例如 2,200円" />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="发布日期">
            <a-input v-model:value="form.release_date" placeholder="例如 2025-01" />
          </a-form-item>
        </a-col>
      </a-row>
      
      <a-form-item label="URL" :rules="[{ required: true }]">
        <a-input v-model:value="form.url" placeholder="产品链接" />
      </a-form-item>
      
      <a-row :gutter="24">
        <a-col :span="12">
          <a-form-item label="标签">
            <a-input v-model:value="form.product_tag" placeholder="产品标签" />
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="系列">
            <a-input v-model:value="form.series" placeholder="所属系列" />
          </a-form-item>
        </a-col>
      </a-row>
      
      <a-form-item label="正文内容（HTML）">
        <a-textarea v-model:value="form.article_content" :rows="8" placeholder="产品介绍HTML内容" />
      </a-form-item>
      
      <a-form-item>
        <a-space>
          <a-button @click="()=>router.back()">取消</a-button>
          <a-button type="primary" :loading="loading" @click="onSubmit">
            {{ isCreate ? '创建' : '保存' }}
          </a-button>
        </a-space>
      </a-form-item>
    </a-form>
  </a-card>
</template>

<style scoped>
</style>


