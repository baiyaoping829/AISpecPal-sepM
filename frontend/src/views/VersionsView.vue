<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const versions = ref([])
const loading = ref(false)

// 模拟数据
versions.value = [
  { id: 1, specification_id: 1, version_number: '1.0', change_log: '初始版本', is_current: 1, created_at: '2024-01-01' },
  { id: 2, specification_id: 1, version_number: '1.1', change_log: '更新部分条款', is_current: 0, created_at: '2024-02-01' }
]
</script>

<template>
  <div class="versions-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>版本管理</span>
          <el-button type="primary">添加版本</el-button>
        </div>
      </template>
      <el-table :data="versions" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="specification_id" label="规范标准ID" />
        <el-table-column prop="version_number" label="版本号" />
        <el-table-column prop="change_log" label="变更记录" />
        <el-table-column prop="is_current" label="是否当前版本">
          <template #default="scope">
            <el-tag v-if="scope.row.is_current === 1" type="success">是</el-tag>
            <el-tag v-else type="info">否</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column label="操作" width="180">
          <template #default="scope">
            <el-button type="primary" size="small">编辑</el-button>
            <el-button type="danger" size="small">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<style scoped>
.versions-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>