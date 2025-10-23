<script setup lang="ts">
import { ref, reactive } from 'vue'
import { api } from '../api'
import { message } from 'ant-design-vue'

const report = ref<any>(null)
const zipFile = ref<File | null>(null)
const zipLoading = ref(false)

async function run() {
  try {
    const res = await api.importFromJson()
    report.value = res
    message.success(`导入完成，新增 ${res.created}，更新 ${res.updated}`)
  } catch (e: any) {
    message.error(e.message || '导入失败')
  }
}

async function uploadZip() {
  if (!zipFile.value) {
    message.warning('请选择ZIP文件')
    return
  }
  try {
    zipLoading.value = true
    const res = await api.importFromZip(zipFile.value)
    report.value = res
    message.success(`导入完成，新增 ${res.created}，更新 ${res.updated}`)
    zipFile.value = null
  } catch (e: any) {
    message.error(e.message || '上传失败')
  } finally {
    zipLoading.value = false
  }
}

const beforeZipUpload = (file: File) => { 
  zipFile.value = file
  return false 
}

// 手动导入
const form = reactive<any>({
  product_name: '',
  price: '',
  release_date: '',
  url: '',
  product_tag: '',
  series: '',
  article_content: '',
})
const imageFile = ref<File | null>(null)
const beforeUpload = (file: File) => { imageFile.value = file; return false }
const manualLoading = ref(false)
async function manualImport() {
  try {
    manualLoading.value = true
    const created: any = await api.createProduct({ ...form })
    if (created && created.id && imageFile.value) {
      await api.uploadImage(created.id, imageFile.value)
      message.success('已创建并上传图片')
    } else if (created && created.id) {
      message.success('已创建产品')
    } else {
      message.warning('已创建（或已存在），如需上传图片请前往图片页')
    }
  } catch (e: any) {
    message.error(e.message || '手动导入失败')
  } finally {
    manualLoading.value = false
  }
}
</script>

<template>
  <a-card title="批量导入 - ZIP压缩包">
    <p>上传包含产品目录的ZIP文件，系统会自动扫描包含 product_details.json 的子目录并导入。</p>
    <a-upload :beforeUpload="beforeZipUpload" :maxCount="1" accept=".zip" :showUploadList="true">
      <a-button type="primary">选择ZIP文件</a-button>
    </a-upload>
    <a-button type="primary" :loading="zipLoading" @click="uploadZip" style="margin-top:12px;">开始导入</a-button>
    <div v-if="report" style="margin-top:16px;">
      <div>总数：{{ report.total }}，新增：{{ report.created }}，更新：{{ report.updated }}</div>
      <template v-if="report.errors?.length">
        <div>错误：</div>
        <a-list size="small" bordered :data-source="report.errors">
          <template #renderItem="{ item }">
            <a-list-item>{{ item }}</a-list-item>
          </template>
        </a-list>
      </template>
    </div>
  </a-card>

  <a-card title="单个导入 - JSON文件" style="margin-top:16px;">
    <p>从后端 DATA_DIR 下的 product_details.json 读取并 UPSERT（按 URL）。</p>
    <a-button type="primary" @click="run">执行导入</a-button>
  </a-card>

  <a-card title="手动导入" style="margin-top:16px;">
    <a-form layout="vertical" :model="form">
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
        <a-textarea v-model:value="form.article_content" :rows="4" />
      </a-form-item>
      <a-form-item label="首图（可选，提交后上传）">
        <a-upload :beforeUpload="beforeUpload" :maxCount="1" :showUploadList="true">
          <a-button>选择图片</a-button>
        </a-upload>
      </a-form-item>
      <a-button type="primary" :loading="manualLoading" @click="manualImport">提交创建并上传</a-button>
    </a-form>
  </a-card>
</template>

<style scoped>
</style>


