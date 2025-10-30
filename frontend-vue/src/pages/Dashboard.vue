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
    <a-row :gutter="[16, 16]">
      <a-col :xs="24" :sm="12" :md="8">
        <a-card :bordered="false" class="stat-card">
          <a-statistic 
            title="产品总数" 
            :value="data.products_total"
            :value-style="{ color: '#1890ff', fontSize: '32px' }">
            <template #prefix>
              <span style="font-size:24px;">📦</span>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="8">
        <a-card :bordered="false" class="stat-card">
          <a-statistic 
            title="有图片" 
            :value="data.with_images"
            :value-style="{ color: '#52c41a', fontSize: '32px' }">
            <template #prefix>
              <span style="font-size:24px;">✅</span>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :xs="24" :sm="12" :md="8">
        <a-card :bordered="false" class="stat-card">
          <a-statistic 
            title="无图片" 
            :value="data.without_images"
            :value-style="{ color: '#faad14', fontSize: '32px' }">
            <template #prefix>
              <span style="font-size:24px;">⚠️</span>
            </template>
          </a-statistic>
        </a-card>
      </a-col>
      <a-col :span="24">
        <a-card title="最近导入的产品" :bordered="false" style="margin-top:16px;">
          <a-table 
            :dataSource="data.recent" 
            :pagination="false" 
            rowKey="id" 
            size="small"
            :columns="[
              { title: '名称', dataIndex: 'product_name', key: 'product_name' },
              { title: '价格', dataIndex: 'price' },
              { title: '发布日期', dataIndex: 'release_date' },
              { title: '标签', dataIndex: 'product_tag' },
              { title: '系列', dataIndex: 'series' },
            ]">
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'product_name'">
                {{ record.product_name_cn || record.product_name }}
              </template>
            </template>
          </a-table>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<style scoped>
.stat-card {
  transition: all 0.3s;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.09);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}
</style>


