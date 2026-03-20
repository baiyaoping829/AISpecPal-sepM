<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'

const files = ref([])
const loading = ref(false)

// 模拟数据
files.value = [
  { id: 1, file_name: 'GB 50010-2010.pdf', file_size: '1.2MB', file_path: '/standards/specs/GB_50010-2010.pdf', uploaded_at: '2024-01-01' },
  { id: 2, file_name: 'GB 50016-2014.pdf', file_size: '1.5MB', file_path: '/standards/specs/GB_50016-2014.pdf', uploaded_at: '2024-02-01' }
]

const handleFileUpload = (file) => {
  ElMessage.success('文件上传成功')
  console.log('Uploaded file:', file)
}
</script>

<template>
  <div class="files-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>文件管理</span>
          <el-upload
            class="upload-demo"
            action="#"
            :auto-upload="false"
            :on-change="handleFileUpload"
          >
            <el-button type="primary">
              <el-icon><Upload /></el-icon>
              上传文件
            </el-button>
          </el-upload>
        </div>
      </template>
      <el-table :data="files" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="file_name" label="文件名" />
        <el-table-column prop="file_size" label="文件大小" />
        <el-table-column prop="uploaded_at" label="上传时间" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="primary" size="small">下载</el-button>
            <el-button type="danger" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.files-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>