<script setup lang="ts">
import { ref, reactive } from 'vue'
import { api } from '../api'
import { message } from 'ant-design-vue'

const report = ref<any>(null)
const zipFile = ref<File | null>(null)
const zipLoading = ref(false)
const modalVisible = ref(false)

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

// 手动导入 - 在弹窗中
const form = reactive<any>({
  product_name: '',
  price: '',
  release_date: '',
  url: '',
  product_tag: '',
  series: '',
  article_content: '',
})
const imageFiles = ref<File[]>([])
const uploadFileList = ref<any[]>([])

const beforeUpload = (file: File) => { 
  // 避免重复添加
  if (!imageFiles.value.find(f => f.name === file.name && f.size === file.size)) {
    imageFiles.value.push(file)
    // 更新显示列表
    uploadFileList.value.push({
      uid: `${Date.now()}-${Math.random()}`,
      name: file.name,
      status: 'done',
      originFileObj: file,
    })
  }
  return false 
}

const handleRemove = (file: any) => {
  // 从imageFiles中移除对应的文件
  const index = imageFiles.value.findIndex(f => f.name === file.name && f.size === file.size)
  if (index > -1) {
    imageFiles.value.splice(index, 1)
  }
  // 从uploadFileList中移除
  const listIndex = uploadFileList.value.findIndex(item => item.uid === file.uid)
  if (listIndex > -1) {
    uploadFileList.value.splice(listIndex, 1)
  }
}

const manualLoading = ref(false)

async function manualImport() {
  let createdProduct = null
  try {
    manualLoading.value = true
    createdProduct = await api.createProduct({ ...form })
    console.log('Created product:', createdProduct)
    console.log('Image files:', imageFiles.value)
    
    if (createdProduct && createdProduct.id && imageFiles.value.length > 0) {
      // 按文件名排序
      const sortedFiles = [...imageFiles.value].sort((a, b) => a.name.localeCompare(b.name))
      console.log('Sorted files:', sortedFiles.map(f => f.name))
      
      // 上传第一张图片时标记为封面图
      try {
        let uploadedCount = 0
        for (let i = 0; i < sortedFiles.length; i++) {
          const file = sortedFiles[i]
          console.log(`Uploading file ${i + 1}/${sortedFiles.length}: ${file.name}, is_cover=${i === 0}`)
          try {
            if (i === 0) {
              // 第一张图片需要标记为封面图
              await api.uploadImageWithCover(createdProduct.id, file, true)
            } else {
              await api.uploadImage(createdProduct.id, file)
            }
            uploadedCount++
            console.log(`Successfully uploaded ${uploadedCount}/${sortedFiles.length} images`)
          } catch (fileError: any) {
            console.error(`Failed to upload file ${file.name}:`, fileError)
            throw fileError
          }
        }
        message.success(`已创建并上传 ${sortedFiles.length} 张图片`)
      } catch (uploadError: any) {
        // 图片上传失败，删除刚创建的产品
        console.error('Image upload failed:', uploadError)
        console.log('Attempting to delete product:', createdProduct.id)
        if (createdProduct && createdProduct.id) {
          try {
            const deleteResult = await api.deleteProduct(createdProduct.id)
            console.log('Product deleted successfully:', deleteResult)
          } catch (deleteError: any) {
            console.error('Failed to delete product:', deleteError)
            message.error(`图片上传失败，且无法删除已创建的产品: ${deleteError.message}`)
          }
        }
        // 重新抛出图片上传错误
        throw uploadError
      }
    } else if (createdProduct && createdProduct.id) {
      message.success('已创建产品')
    } else {
      message.warning('已创建（或已存在），如需上传图片请前往图片页')
    }
    // 清空表单并关闭弹窗
    Object.keys(form).forEach(key => form[key] = '')
    imageFiles.value = []
    uploadFileList.value = []
    modalVisible.value = false
  } catch (e: any) {
    message.error(e.message || '手动导入失败')
  } finally {
    manualLoading.value = false
  }
}

function openModal() {
  // 打开弹窗时清空文件列表
  imageFiles.value = []
  uploadFileList.value = []
  modalVisible.value = true
}

function closeModal() {
  modalVisible.value = false
  // 重置表单
  Object.keys(form).forEach(key => form[key] = '')
  imageFiles.value = []
  uploadFileList.value = []
}
</script>

<template>
  <div class="import-container">
    <!-- 页眉标题 -->
    <div class="page-header">
      <h2>产品导入</h2>
    </div>

    <!-- 导入选项 -->
    <div class="import-grid">
      <!-- ZIP批量导入卡片 -->
      <a-card class="import-card zip-card" :bordered="false">
        <h3>批量导入 ZIP</h3>
        <p class="card-desc">上传包含产品目录的ZIP文件，系统会自动扫描包含 product_details.json 的子目录并导入。</p>
        
        <a-upload :beforeUpload="beforeZipUpload" :maxCount="1" accept=".zip" :showUploadList="true">
          <template #default>
            <div class="upload-area">
              <div class="upload-text">点击选择ZIP文件</div>
              <div class="upload-hint">仅支持 .zip 格式</div>
            </div>
          </template>
        </a-upload>
        
        <a-button 
          type="primary" 
          size="large" 
          :loading="zipLoading" 
          @click="uploadZip" 
          class="action-button"
          :disabled="!zipFile">
          开始导入
        </a-button>
      </a-card>

      <!-- 手动导入卡片 -->
      <a-card class="import-card manual-card" :bordered="false">
        <h3>手动单个导入</h3>
        <p class="card-desc">通过表单逐项输入产品信息，支持上传产品图片。</p>
        
        <div class="card-action-area">
          <a-button 
            type="primary" 
            size="large" 
            @click="openModal"
            class="action-button">
            添加新产品
          </a-button>
        </div>
      </a-card>
    </div>

    <!-- 导入结果报告 -->
    <a-card v-if="report" class="result-card" :bordered="false">
        <template #title>
          <span class="result-title">导入结果</span>
        </template>
      
      <div class="result-stats">
        <div class="stat-item">
          <div class="stat-number">{{ report.total }}</div>
          <div class="stat-label">总数</div>
        </div>
        <div class="stat-item success">
          <div class="stat-number">{{ report.created }}</div>
          <div class="stat-label">新增</div>
        </div>
        <div class="stat-item warning">
          <div class="stat-number">{{ report.updated }}</div>
          <div class="stat-label">更新</div>
        </div>
      </div>
      
      <template v-if="report.errors?.length">
        <a-divider />
        <a-alert type="warning" show-icon style="margin-bottom:16px;">
          <template #message>⚠️ 发现 {{ report.errors.length }} 个错误</template>
        </a-alert>
        <a-list size="small" bordered :data-source="report.errors">
          <template #renderItem="{ item }">
            <a-list-item style="color:#ff4d4f;">{{ item }}</a-list-item>
          </template>
        </a-list>
      </template>
    </a-card>

    <!-- 手动导入弹窗 -->
    <a-modal
      v-model:open="modalVisible"
      title="添加新产品"
      width="800px"
      :footer="null"
      @cancel="closeModal">
      <a-form layout="vertical" :model="form" class="manual-form">
        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="产品名称" :rules="[{ required: true }]">
              <a-input v-model:value="form.product_name" placeholder="请输入产品名称" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="价格">
              <a-input v-model:value="form.price" placeholder="例如 2,200円" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-row :gutter="16">
          <a-col :span="12">
            <a-form-item label="发布日期">
              <a-input v-model:value="form.release_date" placeholder="例如 2025-01" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="标签">
              <a-input v-model:value="form.product_tag" placeholder="产品标签" />
            </a-form-item>
          </a-col>
        </a-row>

        <a-form-item label="产品URL" :rules="[{ required: true }]">
          <a-input v-model:value="form.url" placeholder="请输入产品URL" />
        </a-form-item>

        <a-form-item label="系列">
          <a-input v-model:value="form.series" placeholder="产品系列" />
        </a-form-item>

        <a-form-item label="正文内容 (HTML)">
          <a-textarea v-model:value="form.article_content" :rows="6" placeholder="请输入产品描述或内容..." />
        </a-form-item>

        <a-form-item label="产品图片">
          <a-upload 
            :beforeUpload="beforeUpload" 
            :showUploadList="true" 
            multiple
            :fileList="uploadFileList"
            @remove="handleRemove">
            <a-button>选择图片</a-button>
          </a-upload>
          <div class="upload-hint-text">可选，支持多张图片，第一张将作为封面图</div>
        </a-form-item>

        <div class="modal-actions">
          <a-button @click="closeModal">取消</a-button>
          <a-button type="primary" :loading="manualLoading" @click="manualImport">
            {{ manualLoading ? '提交中...' : '提交创建' }}
          </a-button>
        </div>
      </a-form>
    </a-modal>
  </div>
</template>

<style scoped>
.import-container {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

/* 页眉标题 */
.page-header {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.page-header h2 {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: #262626;
}

/* 导入卡片网格 */
.import-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.import-card {
  transition: all 0.2s ease;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.import-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.import-card h3 {
  font-size: 18px;
  font-weight: 600;
  color: #262626;
  text-align: center;
  margin: 0 0 12px 0;
}

.card-desc {
  color: #595959;
  text-align: center;
  margin-bottom: 24px;
  font-size: 14px;
  line-height: 1.6;
}

/* 上传区域 */
.import-card :deep(.ant-upload) {
  width: 100%;
}

.import-card :deep(.ant-upload .ant-upload-select) {
  width: 100%;
}

.import-card :deep(.ant-upload-list) {
  width: 100%;
}

.upload-area {
  width: 100%;
  box-sizing: border-box;
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 32px;
  text-align: center;
  background: #fafafa;
  cursor: pointer;
  transition: all 0.2s ease;
}

.upload-area:hover {
  border-color: #1890ff;
  background: #f0f7ff;
}

.upload-text {
  color: #262626;
  font-size: 15px;
  font-weight: 500;
  margin-bottom: 8px;
}

.upload-hint {
  color: #8c8c8c;
  font-size: 12px;
}

/* 操作按钮 */
.action-button {
  width: 100%;
  height: 40px;
  font-size: 15px;
  margin-top: 16px;
}

.card-action-area {
  margin-top: 24px;
}

/* 结果卡片 */
.result-card {
  margin-top: 24px;
  border-radius: 8px;
  border: 1px solid #e8e8e8;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.result-title {
  font-size: 16px;
  font-weight: 600;
}

.result-stats {
  display: flex;
  gap: 16px;
  justify-content: center;
  padding: 20px 0;
}

.stat-item {
  text-align: center;
  padding: 16px 24px;
  border-radius: 6px;
  background: #fafafa;
  border: 1px solid #e8e8e8;
  min-width: 100px;
}

.stat-item.success {
  background: #f6ffed;
  border-color: #b7eb8f;
}

.stat-item.warning {
  background: #fffbe6;
  border-color: #ffe58f;
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #262626;
  margin-bottom: 6px;
}

.stat-item.success .stat-number {
  color: #52c41a;
}

.stat-item.warning .stat-number {
  color: #faad14;
}

.stat-label {
  font-size: 13px;
  color: #8c8c8c;
}

/* 弹窗表单 */
.manual-form {
  padding: 8px 0;
}

.upload-hint-text {
  font-size: 12px;
  color: #999;
  margin-top: 8px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .import-grid {
    grid-template-columns: 1fr;
  }
  
  .result-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .stat-item {
    width: 100%;
  }
}
</style>


