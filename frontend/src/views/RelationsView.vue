<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const relations = ref([])
const loading = ref(false)

// 模拟数据
relations.value = [
  { id: 1, source_id: 1, target_id: 2, relation_type: 'reference', description: '参考关系', created_at: '2024-01-01' },
  { id: 2, source_id: 2, target_id: 3, relation_type: 'supplement', description: '补充关系', created_at: '2024-02-01' }
]
</script>

<template>
  <div class="relations-container">
    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <span>关联关系管理</span>
          <el-button type="primary">添加关联关系</el-button>
        </div>
      </template>
      <el-table :data="relations" style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="source_id" label="源规范ID" />
        <el-table-column prop="target_id" label="目标规范ID" />
        <el-table-column prop="relation_type" label="关联类型" />
        <el-table-column prop="description" label="描述" />
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
.relations-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>