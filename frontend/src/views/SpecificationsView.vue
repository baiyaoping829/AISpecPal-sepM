<script setup>
import { ref, onMounted } from 'vue'
import { specificationsAPI } from '../api'
import { ElMessage, ElMessageBox } from 'element-plus'

const specifications = ref([])
const loading = ref(false)

const fetchSpecifications = async () => {
  loading.value = true
  try {
    const response = await specificationsAPI.getList()
    specifications.value = response.data
  } catch (error) {
    ElMessage.error('获取规范标准列表失败')
    console.error('Fetch specifications error:', error)
  } finally {
    loading.value = false
  }
}

const handleDelete = async (id) => {
  try {
    await ElMessageBox.confirm('确定要删除这条记录吗？', '警告', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    await specificationsAPI.delete(id)
    ElMessage.success('删除成功')
    fetchSpecifications()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
      console.error('Delete error:', error)
    }
  }
}

onMounted(() => {
  fetchSpecifications()
})
</script>

<template>
  <div class="specifications-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>规范标准管理</span>
          <el-button type="primary">添加规范标准</el-button>
        </div>
      </template>
      <el-table :data="specifications" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="名称" />
        <el-table-column prop="code" label="编号" />
        <el-table-column prop="type" label="类型" />
        <el-table-column prop="level" label="级别" />
        <el-table-column prop="status" label="状态" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="primary" size="small">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(scope.row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.specifications-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>