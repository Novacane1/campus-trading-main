<template>
  <div class="app-container">
    <header class="app-header" :class="{ 'scrolled': isScrolled }">
      <div class="header-content">
        <div class="logo">
          <router-link to="/" class="logo-link">
            <el-icon class="logo-icon"><ShoppingCartFull /></el-icon>
            <div class="logo-info">
              <h1 class="logo-text">校园二手交易</h1>
              <span class="logo-subtitle">Campus Trade DOS</span>
            </div>
          </router-link>
        </div>
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="搜索商品、分类或用户"
            :prefix-icon="Search"
            @keyup.enter="handleSearch"
            class="search-input"
          >
            <template #append>
              <el-button type="primary" @click="handleSearch" class="search-button">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>
        <nav class="nav-menu">
          <!-- 主题切换 -->
          <button class="theme-toggle" @click="toggleTheme" :title="isDark ? '切换到荧光绿主题' : '切换到琥珀主题'">
            <el-icon v-if="isDark"><Sunny /></el-icon>
            <el-icon v-else><Moon /></el-icon>
          </button>

          <router-link to="/" class="nav-item" active-class="active">
            <el-icon><HomeFilled /></el-icon>
            <span>首页</span>
          </router-link>
          <router-link to="/products" class="nav-item" active-class="active">
            <el-icon><Goods /></el-icon>
            <span>全部商品</span>
          </router-link>
          <router-link to="/categories" class="nav-item" active-class="active">
            <el-icon><MenuIcon /></el-icon>
            <span>分类</span>
          </router-link>
          <router-link to="/dashboard" class="nav-item" active-class="active">
            <el-icon><View /></el-icon>
            <span>可视化</span>
          </router-link>
          <router-link to="/publish" class="nav-item publish-item">
            <el-icon><Plus /></el-icon>
            <span>发布</span>
          </router-link>
          <router-link to="/chat" class="nav-item" active-class="active">
            <el-icon><Bell /></el-icon>
            <span>消息</span>
            <span class="message-badge" v-if="unreadCount > 0">{{ unreadCount }}</span>
          </router-link>
          <router-link to="/cart" class="nav-item" active-class="active" v-if="isLoggedIn">
            <el-icon><ShoppingCart /></el-icon>
            <span>购物车</span>
          </router-link>
          <div class="user-menu" v-if="isLoggedIn">
            <el-dropdown trigger="click">
              <div class="user-avatar-wrapper">
                <span class="user-avatar">
                  {{ userInfo.username?.charAt(0).toUpperCase() || 'U' }}
                </span>
                <el-icon class="dropdown-arrow"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu class="user-dropdown">
                  <router-link to="/profile" class="dropdown-item">
                    <el-icon><User /></el-icon>
                    <span>个人中心</span>
                  </router-link>
                  <router-link to="/my-products" class="dropdown-item">
                    <el-icon><Goods /></el-icon>
                    <span>我的商品</span>
                  </router-link>
                  <router-link to="/orders" class="dropdown-item">
                    <el-icon><List /></el-icon>
                    <span>订单管理</span>
                  </router-link>
                  <router-link to="/favorites" class="dropdown-item">
                    <el-icon><Star /></el-icon>
                    <span>我的收藏</span>
                  </router-link>
                  <router-link to="/history" class="dropdown-item">
                    <el-icon><View /></el-icon>
                    <span>浏览历史</span>
                  </router-link>
                  <router-link v-if="userInfo.role === 'admin'" to="/admin" class="dropdown-item admin-item">
                    <el-icon><Monitor /></el-icon>
                    <span>管理后台</span>
                  </router-link>
                  <el-dropdown-item class="logout-item" @click="handleLogout">
                    <el-icon><SwitchButton /></el-icon>
                    <span>退出登录</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
          <router-link to="/login" class="nav-item login-item" v-else>
            <el-icon><User /></el-icon>
            <span>登录</span>
          </router-link>
        </nav>
      </div>
    </header>
    
    <main class="app-main">
      <router-view v-slot="{ Component }">
        <transition name="page-fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
    
    <footer class="app-footer">
      <div class="footer-content">
        <div class="footer-section animate-fade-in-up delay-100">
          <div class="footer-logo">
            <h3 class="footer-logo-text">校园二手交易</h3>
            <p class="footer-logo-subtitle">Campus Trade</p>
          </div>
          <p class="footer-description">
            为大学生提供安全、便捷的二手交易平台，促进校园资源循环利用，
            营造绿色环保的校园生活环境。
          </p>
          <div class="footer-social">
            <a href="#" class="social-link hover-lift" title="微信">
              <el-icon><ChatLineRound /></el-icon>
            </a>
            <a href="#" class="social-link hover-lift" title="相机">
              <el-icon><Camera /></el-icon>
            </a>
            <a href="#" class="social-link hover-lift" title="消息">
              <el-icon><Message /></el-icon>
            </a>
          </div>
        </div>
        <div class="footer-section animate-fade-in-up delay-200">
          <h4 class="footer-section-title">快速链接</h4>
          <ul class="footer-links">
            <li><router-link to="/" class="footer-link">首页</router-link></li>
            <li><router-link to="/products" class="footer-link">全部商品</router-link></li>
            <li><router-link to="/categories" class="footer-link">商品分类</router-link></li>
            <li><router-link to="/locations" class="footer-link">交易地点</router-link></li>
          </ul>
        </div>
        <div class="footer-section animate-fade-in-up delay-300">
          <h4 class="footer-section-title">关于我们</h4>
          <ul class="footer-links">
            <li><router-link to="/about" class="footer-link">平台介绍</router-link></li>
            <li><router-link to="/dashboard" class="footer-link">数据统计</router-link></li>
            <li><router-link to="/terms" class="footer-link">使用条款</router-link></li>
            <li><router-link to="/privacy" class="footer-link">隐私政策</router-link></li>
          </ul>
        </div>
        <div class="footer-section animate-fade-in-up delay-400">
          <h4 class="footer-section-title">联系方式</h4>
          <ul class="footer-contact">
            <li>
              <el-icon><Message /></el-icon>
              <span>contact@campustrade.com</span>
            </li>
            <li>
              <el-icon><Phone /></el-icon>
              <span>123-4567-8910</span>
            </li>
            <li>
              <el-icon><Location /></el-icon>
              <span>某某大学科技园A座1001室</span>
            </li>
          </ul>
        </div>
      </div>
      <div class="footer-bottom animate-fade-in-up delay-500">
        <p class="footer-copyright">&copy; {{ new Date().getFullYear() }} 校园二手交易系统. 保留所有权利.</p>
        <p class="footer-motto">让闲置物品找到新主人，让校园生活更美好</p>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from './stores/user'
import {
  Search,
  ShoppingCartFull,
  ShoppingCart,
  HomeFilled,
  Menu as MenuIcon,
  Plus,
  Bell,
  User,
  Goods,
  Star,
  View,
  List,
  SwitchButton,
  ArrowDown,
  Moon,
  Sunny,
  Monitor,
  ChatLineRound,
  Camera,
  Message,
  Location,
  Phone
} from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()
const searchQuery = ref('')
const isScrolled = ref(false)
const unreadCount = ref(0)
let unreadTimer = null

const fetchUnreadCount = async () => {
  if (!isLoggedIn.value) {
    unreadCount.value = 0
    return
  }
  try {
    const { default: chatAPI } = await import('./services/chatAPI')
    const res = await chatAPI.getUnreadCount()
    unreadCount.value = res.data.count || 0
  } catch (e) {
    // ignore
  }
}

const isDark = ref(localStorage.getItem('theme') === 'dark')

const toggleTheme = () => {
  isDark.value = !isDark.value
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light')
}

watch(isDark, (val) => {
  if (val) {
    document.documentElement.classList.add('dark')
  } else {
    document.documentElement.classList.remove('dark')
  }
}, { immediate: true })

const isLoggedIn = computed(() => userStore.isLoggedIn)
const userInfo = computed(() => userStore.userInfo)

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { keyword: searchQuery.value } })
  }
}

const handleLogout = () => {
  userStore.logout()
  router.push('/login')
}

const handleScroll = () => {
  isScrolled.value = window.scrollY > 50
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  fetchUnreadCount()
  unreadTimer = setInterval(fetchUnreadCount, 10000)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
  if (unreadTimer) clearInterval(unreadTimer)
})
</script>

<style scoped>
.app-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
}

.app-header {
  position: sticky;
  top: 0;
  z-index: 1200;
  backdrop-filter: blur(18px);
  -webkit-backdrop-filter: blur(18px);
  background: var(--glass-bg);
  border-bottom: 1px solid var(--glass-border);
  box-shadow: 0 10px 30px var(--black-alpha-10);
  transition: all var(--transition-normal);
}

.app-header::after {
  content: '';
  position: absolute;
  left: 50%;
  bottom: -1px;
  width: min(88vw, 960px);
  height: 1px;
  transform: translateX(-50%);
  background: linear-gradient(90deg, transparent, var(--primary-alpha-45), transparent);
  pointer-events: none;
}

.app-header.scrolled {
  box-shadow: 0 14px 34px var(--black-alpha-10);
}

.header-content {
  width: min(var(--container-width), calc(100% - var(--container-padding) * 2));
  margin: 0 auto;
  padding: 0;
  display: flex;
  align-items: center;
  gap: 20px;
  min-height: 84px;
  position: relative;
  transition: min-height var(--transition-normal);
}

.logo {
  flex-shrink: 0;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  color: inherit;
  transition: transform var(--transition-normal);
}

.logo-icon {
  width: 42px;
  height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  font-size: 22px;
  color: #fff;
  background: var(--gradient-primary);
  box-shadow: 0 10px 22px var(--primary-alpha-30);
  transition: transform var(--transition-normal), box-shadow var(--transition-normal);
}

.logo-link:hover .logo-icon {
  transform: translateY(-2px) rotate(-6deg);
  box-shadow: 0 14px 28px var(--primary-alpha-40);
}

.logo-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  letter-spacing: -0.02em;
  line-height: 1.1;
}

.logo-subtitle {
  font-size: 11px;
  color: var(--text-tertiary);
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.search-box {
  width: clamp(220px, 24vw, 320px);
  min-width: 220px;
  margin-left: 14px;
  margin-right: 0;
}

.search-input {
  width: 100%;
}

:deep(.search-input .el-input__wrapper) {
  min-height: 40px;
  border-radius: 4px 0 0 4px !important;
  padding-left: 12px !important;
  border: 1px solid var(--border-primary) !important;
  border-right: none !important;
  box-shadow: none !important;
  background: var(--bg-input) !important;
}

:deep(.search-input .el-input__inner) {
  color: var(--text-primary) !important;
  font-size: 13px;
}

:deep(.search-input .el-input-group__append) {
  background: var(--bg-input) !important;
  border: 1px solid var(--primary-color) !important;
  border-left: none !important;
  border-radius: 0 4px 4px 0 !important;
  box-shadow: none !important;
  padding: 0 !important;
  display: flex !important;
  align-items: stretch !important;
  min-width: 44px;
  width: auto !important;
  flex: 0 0 auto;
}

:deep(.search-input .el-input-group__append .el-button) {
  height: 100% !important;
  min-height: 40px !important;
  min-width: 44px !important;
  margin: 0 !important;
  padding: 0 10px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.search-button {
  min-height: 40px;
  border-radius: 0 4px 4px 0;
  padding: 0 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--gradient-primary) !important;
  border-color: transparent !important;
  color: white !important;
  transition: filter var(--transition-fast);
}

.search-button:hover {
  filter: brightness(1.05);
}

.nav-menu {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: auto;
  flex-wrap: nowrap;
  min-width: fit-content;
  overflow-x: auto;
  scrollbar-width: none;
}

.nav-menu::-webkit-scrollbar {
  display: none;
}

.theme-toggle {
  width: 36px;
  height: 36px;
  background: var(--bg-input);
  border: 1px solid var(--border-secondary);
  padding: 0;
  cursor: pointer;
  color: var(--text-tertiary);
  font-size: 18px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 999px;
  transition: all var(--transition-normal);
  margin-right: 2px;
  flex-shrink: 0;
}

.theme-toggle:hover {
  color: var(--primary-color);
  border-color: var(--primary-alpha-45);
  box-shadow: 0 10px 22px var(--primary-alpha-20);
  transform: translateY(-1px);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 0 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  text-decoration: none;
  border-radius: 999px;
  transition: all var(--transition-normal);
  position: relative;
  height: 36px;
  box-sizing: border-box;
  border: 1px solid transparent;
  font-size: 13px;
  font-weight: 500;
  flex-shrink: 0;
}

.publish-item {
  background: var(--gradient-primary);
  color: #fff;
  border-color: transparent;
  box-shadow: 0 10px 22px var(--primary-alpha-28);
}

.login-item {
  border: 1px solid var(--primary-alpha-45);
  color: var(--primary-color);
  background: var(--primary-alpha-06);
}

.nav-item:hover {
  color: var(--primary-color);
  border-color: var(--primary-alpha-35);
  background: var(--primary-alpha-08);
  transform: translateY(-1px);
}

.nav-item.active {
  color: #fff;
  border-color: transparent;
  background: var(--gradient-primary);
  font-weight: 500;
  box-shadow: 0 8px 18px var(--primary-alpha-24);
}

.publish-item:hover {
  color: #fff;
  box-shadow: 0 12px 24px var(--primary-alpha-30);
  filter: brightness(1.04);
}

.login-item:hover {
  color: #fff;
  background: var(--gradient-primary);
  border-color: transparent;
}

.message-badge {
  position: absolute;
  top: -2px;
  right: -2px;
  min-width: 17px;
  height: 17px;
  background: linear-gradient(135deg, #ff6666, #e5484d);
  color: white;
  font-size: 10px;
  font-weight: bold;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 5px;
  transform: translate(50%, -50%);
  box-shadow: 0 8px 18px var(--danger-alpha-12);
}

.user-menu {
  position: relative;
  flex-shrink: 0;
}

.user-avatar-wrapper {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 2px 8px 2px 4px;
  border-radius: 999px;
  border: 1px solid var(--border-secondary);
  background: var(--bg-input);
  transition: all var(--transition-normal);
}

.user-avatar-wrapper:hover {
  border-color: var(--primary-alpha-40);
  box-shadow: 0 10px 20px var(--primary-alpha-20);
}

.user-avatar {
  display: inline-block;
  width: 30px;
  height: 30px;
  border-radius: 50%;
  background: var(--gradient-primary);
  color: white;
  text-align: center;
  line-height: 30px;
  font-weight: 700;
  font-size: 13px;
  transition: transform var(--transition-normal);
}

.user-avatar-wrapper:hover .user-avatar {
  transform: scale(1.05);
}

.dropdown-arrow {
  font-size: 11px;
  color: var(--text-tertiary);
  transition: all var(--transition-normal);
}

.user-avatar-wrapper:hover .dropdown-arrow {
  color: var(--primary-color);
  transform: rotate(180deg) translateY(-1px);
}

.user-dropdown {
  min-width: 198px;
  border-radius: 14px;
  padding: 6px;
  border: 1px solid var(--border-secondary);
  background: var(--bg-elevated);
  box-shadow: var(--shadow-lg);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  margin: 2px 0;
  border-radius: 10px;
  text-decoration: none;
  color: var(--text-secondary);
  transition: all var(--transition-fast);
  font-size: 13px;
  font-weight: 500;
}

.dropdown-item:hover {
  background-color: var(--primary-alpha-08);
  color: var(--primary-color);
}

.admin-item {
  color: var(--danger-color);
}

.admin-item:hover {
  background-color: var(--danger-alpha-12);
}

.logout-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  margin-top: 4px;
  color: var(--danger-color);
  transition: all var(--transition-fast);
  font-weight: 500;
}

.logout-item:hover {
  background-color: var(--danger-alpha-12);
}

.app-main {
  flex: 1;
  width: min(var(--container-width), calc(100% - var(--container-padding) * 2));
  padding: 22px 0 8px;
  margin: 0 auto;
}

.app-footer {
  margin-top: 44px;
  padding: 56px 0 28px;
  background:
    linear-gradient(160deg, var(--primary-alpha-08), transparent),
    var(--bg-primary);
  border-top: 1px solid var(--border-secondary);
  position: relative;
  overflow: hidden;
}

.app-footer::before {
  content: '';
  position: absolute;
  top: -120px;
  right: -120px;
  width: 360px;
  height: 360px;
  border-radius: 50%;
  background: radial-gradient(circle, var(--primary-alpha-10), transparent);
  pointer-events: none;
}

.footer-content,
.footer-bottom {
  width: min(var(--container-width), calc(100% - var(--container-padding) * 2));
  margin: 0 auto;
}

.footer-content {
  position: relative;
  z-index: 1;
  display: grid;
  grid-template-columns: 1.35fr repeat(3, minmax(170px, 1fr));
  gap: 30px;
  margin-bottom: 28px;
}

.footer-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.footer-logo {
  display: inline-flex;
  flex-direction: column;
  gap: 4px;
  margin-bottom: 4px;
}

.footer-logo-text {
  font-size: 20px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
}

.footer-logo-subtitle {
  margin: 0;
  color: var(--text-tertiary);
  font-size: 12px;
  letter-spacing: 0.15em;
  text-transform: uppercase;
}

.footer-description {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
  line-height: 1.75;
  max-width: 340px;
}

.footer-social {
  display: flex;
  gap: 10px;
}

.social-link {
  width: 38px;
  height: 38px;
  border-radius: 12px;
  border: 1px solid var(--border-secondary);
  background: var(--bg-input);
  color: var(--text-tertiary);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-normal);
}

.social-link:hover {
  color: #fff;
  background: var(--gradient-primary);
  border-color: transparent;
  transform: translateY(-2px);
}

.footer-section-title {
  font-size: 15px;
  font-weight: 700;
  margin: 0;
  color: var(--text-primary);
  letter-spacing: 0.02em;
}

.footer-links,
.footer-contact {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-link {
  color: var(--text-secondary);
  font-size: 14px;
  transition: color var(--transition-fast), transform var(--transition-fast);
}

.footer-link:hover {
  color: var(--primary-color);
  transform: translateX(3px);
}

.footer-contact li {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: var(--text-secondary);
  font-size: 14px;
}

.footer-contact li .el-icon {
  margin-top: 2px;
  color: var(--primary-color);
}

.footer-bottom {
  position: relative;
  z-index: 1;
  border-top: 1px solid var(--border-secondary);
  padding-top: 18px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.footer-copyright {
  font-size: 12px;
  color: var(--text-tertiary);
  margin: 0;
}

.footer-motto {
  margin: 0;
  font-size: 12px;
  color: var(--primary-color);
  font-weight: 600;
}

.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.page-fade-enter-from,
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(14px);
}

@media (max-width: 1220px) {
  .search-box {
    width: min(320px, 30vw);
  }

  .nav-item span {
    display: none;
  }

  .nav-item {
    width: 36px;
    padding: 0;
    justify-content: center;
  }

  .message-badge {
    right: 2px;
  }

  .footer-content {
    grid-template-columns: repeat(2, minmax(220px, 1fr));
  }
}

@media (max-width: 900px) {
  .header-content {
    min-height: auto;
    padding: 12px 0;
    flex-wrap: wrap;
    gap: 10px;
  }

  .logo {
    order: 1;
  }

  .nav-menu {
    order: 2;
    width: auto;
    margin-left: auto;
  }

  .search-box {
    order: 3;
    width: 100%;
    min-width: 100%;
    margin: 0;
  }

  .app-main {
    width: calc(100% - var(--container-padding) * 2);
    padding-top: 14px;
  }
}

@media (max-width: 768px) {
  .logo-icon {
    width: 38px;
    height: 38px;
    font-size: 20px;
  }

  .logo-text {
    font-size: 18px;
  }

  .logo-subtitle {
    display: none;
  }

  .nav-menu {
    width: 100%;
    margin-left: 0;
    justify-content: flex-start;
  }

  .theme-toggle {
    margin-right: 4px;
  }

  .footer-content {
    grid-template-columns: 1fr;
    gap: 20px;
  }

  .footer-section {
    align-items: flex-start;
    text-align: left;
  }

  .footer-bottom {
    flex-direction: column;
    align-items: flex-start;
  }
}

@media (max-width: 480px) {
  .header-content {
    gap: 8px;
    padding: 10px 0;
  }

  .nav-menu {
    gap: 4px;
  }

  .nav-item {
    width: 34px;
    height: 34px;
  }

  .user-avatar-wrapper {
    padding-right: 6px;
  }

  .user-avatar {
    width: 28px;
    height: 28px;
    line-height: 28px;
  }

  .app-main {
    width: calc(100% - 20px);
  }

  .app-footer {
    padding: 44px 0 24px;
  }
}

/* WP-DOS inspired overrides */
.app-container {
  color: var(--text-primary);
}

.app-header {
  backdrop-filter: none;
  -webkit-backdrop-filter: none;
  background:
    linear-gradient(var(--header-bg-overlay), var(--header-bg-overlay)),
    url('./assets/dos_noise-texture.png');
  border-bottom: 1px solid var(--border-primary);
  box-shadow: none;
}

.app-header::after {
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--primary-color), transparent);
  opacity: 0.55;
}

.app-header.scrolled {
  box-shadow: none;
}

.header-content {
  min-height: 72px;
  gap: 14px;
}

.logo-link {
  gap: 8px;
}

.logo-icon {
  width: 36px;
  height: 36px;
  border-radius: 4px;
  font-size: 18px;
  color: var(--primary-color);
  background: color-mix(in srgb, var(--bg-primary) 88%, black 12%);
  border: 1px solid var(--border-primary);
  box-shadow: none;
}

.logo-link:hover .logo-icon {
  transform: none;
  box-shadow: none;
  border-color: var(--primary-color);
}

.logo-text {
  font-size: 16px;
  font-weight: 400;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.logo-subtitle {
  font-size: 10px;
  letter-spacing: 0.16em;
}

.search-box {
  width: clamp(220px, 24vw, 320px);
  margin-left: 14px;
  margin-right: 0;
}

:deep(.search-input .el-input__wrapper) {
  min-height: 40px;
  border-radius: 4px 0 0 4px !important;
  padding-left: 12px !important;
  border: 1px solid var(--border-primary) !important;
  border-right: none !important;
  background: var(--bg-input) !important;
}

:deep(.search-input .el-input-group__append) {
  background: var(--bg-input) !important;
  border-radius: 0 4px 4px 0 !important;
  border: 1px solid var(--primary-color) !important;
  border-left: none !important;
  display: flex !important;
  align-items: stretch !important;
  min-width: 44px;
  width: auto !important;
  flex: 0 0 auto;
}

:deep(.search-input .el-input-group__append .el-button) {
  height: 100% !important;
  min-height: 40px !important;
  min-width: 44px !important;
  margin: 0 !important;
  padding: 0 10px !important;
  display: inline-flex !important;
  align-items: center !important;
  justify-content: center !important;
}

.search-button {
  min-height: 40px;
  border-radius: 0 4px 4px 0;
  padding: 0 12px;
  color: var(--bg-primary) !important;
}

.theme-toggle {
  width: 34px;
  height: 34px;
  border-radius: 4px;
  border-color: var(--border-primary);
  background: var(--bg-input);
}

.theme-toggle:hover {
  border-color: var(--primary-color);
  box-shadow: none;
  transform: none;
}

.nav-item {
  height: 34px;
  border-radius: 4px;
  border: 1px solid var(--border-secondary);
  background: var(--bg-elevated);
  color: var(--text-secondary);
  font-size: 12px;
  letter-spacing: 0.04em;
}

.nav-item:hover {
  background: color-mix(in srgb, var(--bg-elevated) 70%, var(--primary-color) 30%);
  border-color: var(--primary-color);
  color: var(--text-primary);
  transform: none;
}

.nav-item.active,
.publish-item {
  color: var(--bg-primary);
  border-color: var(--primary-color);
  background: var(--gradient-primary);
  box-shadow: none;
}

.publish-item:hover,
.login-item:hover {
  color: var(--bg-primary);
  box-shadow: none;
  filter: brightness(1.06);
}

.login-item {
  border-color: var(--border-primary);
  color: var(--text-primary);
  background: var(--bg-input);
}

.message-badge {
  background: var(--danger-color);
  box-shadow: none;
}

.user-avatar-wrapper {
  border-radius: 4px;
  border-color: var(--border-primary);
  background: var(--bg-input);
}

.user-avatar-wrapper:hover {
  box-shadow: none;
  border-color: var(--primary-color);
}

.user-avatar {
  border-radius: 4px;
  width: 28px;
  height: 28px;
  line-height: 28px;
  color: var(--bg-primary);
  box-shadow: none;
}

.user-dropdown {
  border-radius: 4px;
  border: 1px solid var(--border-primary);
  box-shadow: none;
}

.dropdown-item {
  border-radius: 4px;
  font-size: 12px;
}

.dropdown-item:hover {
  background-color: color-mix(in srgb, var(--bg-elevated) 65%, var(--primary-color) 35%);
  color: var(--text-primary);
}

.app-main {
  padding-top: 18px;
}

.app-footer {
  background:
    linear-gradient(var(--footer-bg-overlay), var(--footer-bg-overlay)),
    url('./assets/dos_noise-texture.png');
  border-top: 1px solid var(--border-primary);
}

.app-footer::before {
  background: radial-gradient(circle, var(--footer-glow-color), transparent 70%);
}

.footer-bottom {
  border-top: 1px solid var(--border-primary);
}

.footer-link:hover {
  transform: none;
}
</style>
