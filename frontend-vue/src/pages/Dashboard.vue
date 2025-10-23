<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { api } from '../api'

const data = ref<any>(null)
onMounted(async () => {
  try { data.value = await api.statsOverview(10) } catch {}
})
</script>

<template>
  <div v-if="data">
    <a-row :gutter="16">
      <a-col :span="6">
        <a-card>
          <a-statistic title="产品总数" :value="data.products_total" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="有图" :value="data.with_images" />
        </a-card>
      </a-col>
      <a-col :span="6">
        <a-card>
          <a-statistic title="无图" :value="data.without_images" />
        </a-card>
      </a-col>
      <a-col :span="24" style="margin-top:16px;">
        <a-card title="最近导入">
          <a-table :dataSource="data.recent" :pagination="false" rowKey="id" size="small"
            :columns="[
              { title: '名称', dataIndex: 'product_name' },
              { title: '价格', dataIndex: 'price' },
              { title: '发布日期', dataIndex: 'release_date' },
              { title: '标签', dataIndex: 'product_tag' },
              { title: '系列', dataIndex: 'series' },
            ]"/>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<style scoped>
</style>


