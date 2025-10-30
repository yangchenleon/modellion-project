<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { api } from '../api'
import { message } from 'ant-design-vue'

const router = useRouter()
const loading = ref(false)
const data = ref<{ items: any[]; meta: any }>({ items: [], meta: { page: 1, page_size: 20, total: 0 } })

const name = ref('')
const tag = ref('')
const series = ref('')

async function fetchData(page = 1, page_size = 20) {
  try {
    loading.value = true
    console.log('开始筛选，参数:', { name: name.value, tag: tag.value, series: series.value, page, page_size })
    const res = await api.getProducts({ name: name.value, tag: tag.value, series: series.value, page, page_size })
    data.value = res as any
    console.log('筛选结果:', res)
  } catch (e: any) {
    console.error('筛选失败:', e)
    message.error(e.message)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  console.log('搜索按钮被点击')
  fetchData(1, data.value.meta.page_size)
}

onMounted(() => {
  fetchData()
})

const columns = [
  { title: '名称', dataIndex: 'product_name', key: 'product_name' },
  { title: '价格', dataIndex: 'price' },
  { title: '发布日期', dataIndex: 'release_date' },
  { title: '标签', dataIndex: 'product_tag' },
  { title: '系列', dataIndex: 'series' },
  { title: '操作', key: 'actions' },
]
</script>

<template>
  <a-card :bordered="false" style="box-shadow: 0 2px 8px rgba(0,0,0,0.09);">
    <template #title>
      <span style="font-size:18px;font-weight:500;">📦 产品列表</span>
    </template>
    <template #extra>
      <a-button type="primary" icon="plus" @click="() => router.push('/products/0')">新建产品</a-button>
    </template>
    
    <a-card :bordered="false" style="background:#fafafa;margin-bottom:16px;">
      <a-form layout="inline" :label-col="{ span: 6 }">
        <a-form-item label="名称">
          <a-input v-model:value="name" allow-clear placeholder="包含关键词" style="width:200px;" />
        </a-form-item>
        <a-form-item label="标签">
          <a-input v-model:value="tag" allow-clear style="width:150px;" />
        </a-form-item>
        <a-form-item label="系列">
          <a-input v-model:value="series" allow-clear style="width:150px;" />
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="handleSearch" :loading="loading">搜索</a-button>
        </a-form-item>
      </a-form>
    </a-card>
    
    <a-table :loading="loading" rowKey="id" :dataSource="data.items"
      :pagination="{
        current: data.meta.page,
        total: data.meta.total,
        pageSize: data.meta.page_size,
        onChange: (p,s)=>fetchData(p,s)
      }"
      :columns="columns">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'product_name'">
          {{ record.product_name_cn || record.product_name }}
        </template>
        <template v-if="column.key === 'actions'">
          <a-space>
            <a-button size="small" @click="() => router.push(`/products/${record.id}/detail`)">详情</a-button>
            <a-button size="small" @click="() => router.push(`/products/${record.id}`)">编辑</a-button>
            <a-button size="small" @click="() => router.push(`/images/${record.id}`)">图片</a-button>
            <a-popconfirm title="确认删除？" @confirm="async ()=>{ await api.deleteProduct(record.id); message.success('已删除'); fetchData(data.meta.page, data.meta.page_size); }">
              <a-button size="small" danger>删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>
  </a-card>
</template>

<style scoped>
</style>


