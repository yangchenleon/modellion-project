<script setup lang="ts">
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { api } from '../api'
import { message } from 'ant-design-vue'

const route = useRoute()
const pid = ref<number>(Number(route.params.productId))
const items = ref<any[]>([])

async function load() {
  const res = await api.listImages(pid.value)
  items.value = (res as any) || []
  // 预签名 URL（缩略预览）
  try {
    await Promise.all(
      items.value.map(async (img: any) => {
        try {
          const { url } = await api.presign(img.id)
          img._url = url
        } catch {}
      })
    )
  } catch {}
}

watch(() => route.params.productId, (v) => {
  pid.value = Number(v)
  load()
})

onMounted(() => load())

const handleCustomRequest = async (options: any) => {
  try {
    await api.uploadImage(pid.value, options.file as File)
    message.success('上传成功')
    await load()
    options.onSuccess && options.onSuccess({}, new XMLHttpRequest())
  } catch (e: any) {
    options.onError && options.onError(e)
    message.error(e.message || '上传失败')
  }
}
</script>

<template>
  <a-card :title="`图片管理 #${pid}`">
    <a-upload :showUploadList="false" :customRequest="handleCustomRequest">
      <a-button type="primary">上传图片</a-button>
    </a-upload>

    <div style="display:grid;grid-template-columns:repeat(auto-fill, minmax(200px, 1fr));gap:16px;margin-top:16px;">
      <div v-for="img in items" :key="img.id" class="image-card" :class="{ 'is-cover': img.is_cover }">
        <div class="image-wrapper">
          <div v-if="img.is_cover" class="cover-badge">头像</div>
          <img :alt="img.image_filename" :src="img._url || ''" />
          <div class="image-overlay">
            <a-space direction="vertical" size="small">
              <a-button size="small" block @click="async ()=>{ const url = img._url || (await api.presign(img.id)).url; const w = window.open(url, '_blank'); if(!w) message.info('请允许弹窗以预览') }">预览</a-button>
              <a-button v-if="!img.is_cover" size="small" type="primary" block @click="async ()=>{ await api.setImageAsCover(img.id); message.success('已设为头像'); load(); }">设为头像</a-button>
              <a-popconfirm title="删除该图片？" @confirm="async ()=>{ await api.deleteImage(img.id, true); message.success('已删除'); load(); }">
                <a-button size="small" danger block>删除</a-button>
              </a-popconfirm>
            </a-space>
          </div>
        </div>
      </div>
    </div>
  </a-card>
</template>

<style scoped>
.image-card {
  border: 1px solid #e8e8e8;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.image-card.is-cover {
  border: 2px solid #1890ff;
}

.image-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 100%; /* 1:1 宽高比 */
  background: #fafafa;
}

.image-wrapper img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  background: #1890ff;
  color: #fff;
  padding: 2px 8px;
  font-size: 12px;
  border-radius: 4px;
  z-index: 2;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-card:hover .image-overlay {
  opacity: 1;
}
</style>


