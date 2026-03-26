<template>
  <div class="admin-layout">
    <div class="admin-sidebar">
      <div class="sidebar-logo">
        <el-icon><Monitor /></el-icon>
        <span>管理后台</span>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="admin-menu"
        router
      >
        <el-menu-item index="/admin/dashboard">
          <el-icon><DataAnalysis /></el-icon>
          <span>数据监控</span>
        </el-menu-item>
        <el-menu-item index="/admin/users">
          <el-icon><User /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/products">
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/categories">
          <el-icon><Menu /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/audit">
          <el-icon><Checked /></el-icon>
          <span>审核管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/logs">
          <el-icon><Document /></el-icon>
          <span>系统日志</span>
        </el-menu-item>
        <el-menu-item index="/admin/orders">
          <el-icon><List /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/reviews">
          <el-icon><ChatDotRound /></el-icon>
          <span>评价管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/announcements">
          <el-icon><Bell /></el-icon>
          <span>公告管理</span>
        </el-menu-item>
        <el-menu-item index="/admin/reports">
          <el-icon><Warning /></el-icon>
          <span>举报申诉</span>
        </el-menu-item>
        <el-menu-item index="/admin/banners">
          <el-icon><Picture /></el-icon>
          <span>Banner管理</span>
        </el-menu-item>
      </el-menu>
    </div>
    <div class="admin-main">
      <div class="admin-header">
        <div class="header-left">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item>管理系统</el-breadcrumb-item>
            <el-breadcrumb-item>{{ currentRouteName }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="header-right">
          <el-dropdown>
            <span class="admin-user">
              管理员 <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      <div class="admin-content">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Monitor,
  DataAnalysis,
  User,
  Goods,
  Menu,
  Checked,
  Document,
  ArrowDown,
  List,
  ChatDotRound,
  Bell,
  Warning,
  Picture
} from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const activeMenu = computed(() => route.path)
const currentRouteName = computed(() => {
  const nameMap = {
    '/admin/dashboard': '数据监控',
    '/admin/users': '用户管理',
    '/admin/products': '商品管理',
    '/admin/categories': '分类管理',
    '/admin/audit': '审核管理',
    '/admin/logs': '系统日志',
    '/admin/orders': '订单管理',
    '/admin/reviews': '评价管理',
    '/admin/announcements': '公告管理',
    '/admin/reports': '举报申诉',
    '/admin/banners': 'Banner管理'
  }
  return nameMap[route.path] || '控制台'
})

const logout = () => {
  router.push('/login')
}
</script>

<style scoped>
.admin-layout {
  display: flex;
  height: 100vh;
  background-color: var(--bg-secondary);
}

.admin-sidebar {
  width: 240px;
  background-color: var(--bg-primary);
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
}

.sidebar-logo {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  font-size: 18px;
  font-weight: bold;
  background-color: var(--bg-elevated);
}

.admin-menu {
  border-right: none;
  background-color: transparent;
}

:deep(.el-menu) {
  --el-menu-bg-color: transparent;
  --el-menu-text-color: var(--white-alpha-65);
  --el-menu-hover-bg-color: var(--primary-color);
  --el-menu-active-color: var(--bg-primary);
}

:deep(.el-menu-item.is-active) {
  background-color: var(--primary-color) !important;
}

.admin-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.admin-header {
  height: 64px;
  background-color: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
  box-shadow: 0 1px 4px var(--black-alpha-10);
  z-index: 10;
}

.admin-user {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--text-primary);
}

.admin-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
