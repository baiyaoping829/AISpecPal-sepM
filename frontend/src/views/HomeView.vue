<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import { House, Document, Refresh, Link, Folder } from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

const handleLogout = () => {
  authStore.removeToken()
  ElMessage.success('退出登录成功')
  router.push('/login')
}
</script>

<template>
  <div class="home-container">
    <!-- 导航栏 -->
    <header class="navbar">
      <div class="navbar-brand">
        <h1>工程规范标准管理系统</h1>
      </div>
      <div class="navbar-right">
        <span v-if="authStore.currentUser">欢迎，{{ authStore.currentUser.sub }}</span>
        <el-button type="primary" @click="handleLogout" style="margin-left: 20px">
          退出登录
        </el-button>
      </div>
    </header>

    <!-- 侧边栏 -->
    <div class="sidebar">
      <el-menu
        :default-active="$route.path"
        class="sidebar-menu"
        router
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/specifications">
          <el-icon><Document /></el-icon>
          <span>规范标准管理</span>
        </el-menu-item>
        <el-menu-item index="/versions">
          <el-icon><Refresh /></el-icon>
          <span>版本管理</span>
        </el-menu-item>
        <el-menu-item index="/relations">
          <el-icon><Link /></el-icon>
          <span>关联关系管理</span>
        </el-menu-item>
        <el-menu-item index="/files">
          <el-icon><Folder /></el-icon>
          <span>文件管理</span>
        </el-menu-item>
      </el-menu>
    </div>

    <!-- 主内容区 -->
    <main class="main-content">
      <div class="welcome-section">
        <h2>欢迎使用工程规范标准管理系统</h2>
        <p>本系统用于管理工程规范标准的基本信息、PDF文档和历史版本，建立规范标准之间的关联关系，方便查阅和管理。</p>
        <div class="stats-cards">
          <el-card shadow="hover" class="stat-card">
            <template #header>
              <div class="card-header">
                <span>规范标准数量</span>
              </div>
            </template>
            <div class="stat-number">10</div>
            <div class="stat-desc">已管理的规范标准</div>
          </el-card>
          <el-card shadow="hover" class="stat-card">
            <template #header>
              <div class="card-header">
                <span>版本数量</span>
              </div>
            </template>
            <div class="stat-number">20</div>
            <div class="stat-desc">历史版本记录</div>
          </el-card>
          <el-card shadow="hover" class="stat-card">
            <template #header>
              <div class="card-header">
                <span>关联关系</span>
              </div>
            </template>
            <div class="stat-number">16</div>
            <div class="stat-desc">规范标准之间的关联</div>
          </el-card>
          <el-card shadow="hover" class="stat-card">
            <template #header>
              <div class="card-header">
                <span>文件数量</span>
              </div>
            </template>
            <div class="stat-number">30</div>
            <div class="stat-desc">已上传的PDF文件</div>
          </el-card>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
  height: 60px;
  background-color: #409eff;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.navbar-brand h1 {
  font-size: 18px;
  font-weight: 600;
}

.navbar-right {
  display: flex;
  align-items: center;
}

.sidebar {
  width: 200px;
  background-color: #f0f2f5;
  height: calc(100vh - 60px);
  position: fixed;
  left: 0;
  top: 60px;
  overflow-y: auto;
}

.sidebar-menu {
  height: 100%;
  border-right: none;
}

.main-content {
  margin-left: 200px;
  padding: 20px;
  flex: 1;
  background-color: #f5f5f5;
}

.welcome-section {
  background-color: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.welcome-section h2 {
  margin-bottom: 20px;
  color: #303133;
}

.welcome-section p {
  margin-bottom: 30px;
  color: #606266;
  line-height: 1.5;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
}

.stat-card {
  transition: transform 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-5px);
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  color: #409eff;
  margin: 20px 0;
  text-align: center;
}

.stat-desc {
  text-align: center;
  color: #606266;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>