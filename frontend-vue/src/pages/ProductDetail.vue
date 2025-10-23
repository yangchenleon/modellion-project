<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'

const route = useRoute()
const id = Number(route.params.id)
const product = ref<any>(null)
const images = ref<any[]>([])

// 分离头像和详情图
const coverImage = computed(() => images.value.find(img => img.is_cover))
const detailImages = computed(() => images.value.filter(img => !img.is_cover))

onMounted(async () => {
  product.value = await api.getProduct(id)
  try {
    images.value = await api.listImages(id)
    // 为每张图获取可预览 URL
    await Promise.all(images.value.map(async (img:any)=>{
      try { img._url = (await api.presign(img.id)).url } catch {}
    }))
  } catch {}
})
</script>

<template>
  <a-card v-if="product" :title="(product.product_name_cn || product.product_name) || '详情'">
    <div style="display:flex;gap:24px;">
      <!-- 左侧：产品信息表格 -->
      <div style="flex:1;">
        <a-descriptions bordered :column="1" size="middle">
          <a-descriptions-item label="名称">{{ product.product_name_cn || product.product_name }}</a-descriptions-item>
          <a-descriptions-item v-if="product.product_name_cn" label="日文名称" style="font-size:12px;color:#999;">{{ product.product_name }}</a-descriptions-item>
          <a-descriptions-item label="价格">{{ product.price }}</a-descriptions-item>
          <a-descriptions-item label="发布日期">{{ product.release_date }}</a-descriptions-item>
          <a-descriptions-item label="标签">{{ product.product_tag }}</a-descriptions-item>
          <a-descriptions-item label="系列">{{ product.series }}</a-descriptions-item>
          <a-descriptions-item label="URL"><a :href="product.url" target="_blank">{{ product.url }}</a></a-descriptions-item>
          <a-descriptions-item label="正文" v-if="product.article_content">
            <div v-html="product.article_content"></div>
          </a-descriptions-item>
        </a-descriptions>
      </div>
      
      <!-- 右侧：头像图片 -->
      <div style="width:300px;">
        <div v-if="coverImage && coverImage._url" style="border:1px solid #eee;padding:8px;background:#fff;">
          <img 
            :alt="coverImage.image_filename" 
            :src="coverImage._url" 
            style="width:100%;cursor:pointer;"
            @click="()=>{ if(coverImage._url) window.open(coverImage._url, '_blank') }" 
          />
        </div>
        <div v-else style="border:1px solid #ddd;padding:40px;text-align:center;color:#999;background:#fafafa;">
          暂无头像图片
        </div>
      </div>
    </div>

    <!-- 详情图片 -->
    <div v-if="detailImages.length > 0" style="margin-top:24px;">
      <h3 style="margin-bottom:12px;">详情图片 ({{ detailImages.length }})</h3>
      <div style="display:flex;flex-wrap:wrap;gap:12px;">
        <div v-for="img in detailImages" :key="img.id" style="border:1px solid #eee;padding:8px;">
          <img :alt="img.image_filename" :src="img._url || ''" width="200"
            @click="()=>{ if(img._url) window.open(img._url, '_blank') }" />
        </div>
      </div>
    </div>
  </a-card>
</template>

<style scoped>
</style>


