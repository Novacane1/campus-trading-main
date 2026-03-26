import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('../views/Home.vue'),
    meta: { title: '首页' }
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/auth/Login.vue'),
    meta: { title: '登录' },
    beforeEnter: (to, from, next) => {
      const userStore = useUserStore()
      if (userStore.isLoggedIn) {
        next({ path: '/', replace: true })
      } else {
        next()
      }
    }
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/auth/Register.vue'),
    meta: { title: '注册' },
    beforeEnter: (to, from, next) => {
      const userStore = useUserStore()
      if (userStore.isLoggedIn) {
        next({ path: '/', replace: true })
      } else {
        next()
      }
    }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('../views/auth/ForgotPassword.vue'),
    meta: { title: '找回密码' }
  },
  {
    path: '/product/:id',
    name: 'ProductDetail',
    component: () => import('../views/product/ProductDetail.vue'),
    meta: { title: '商品详情' }
  },
  {
    path: '/products',
    name: 'AllProducts',
    component: () => import('../views/product/AllProducts.vue'),
    meta: { title: '全部商品' }
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue'),
    meta: { title: '数据行情' }
  },
  {
    path: '/market-insights',
    name: 'MarketInsights',
    component: () => import('../views/MarketInsights.vue'),
    meta: { title: '市场洞察' }
  },
  {
    path: '/admin',
    component: () => import('../views/admin/AdminLayout.vue'),
    redirect: '/admin/dashboard',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('../views/admin/AdminDashboard.vue'),
        meta: { title: '管理后台 - 数据监控' }
      },
      {
        path: 'users',
        name: 'UserManagement',
        component: () => import('../views/admin/UserManagement.vue'),
        meta: { title: '管理后台 - 用户管理' }
      },
      {
        path: 'products',
        name: 'ProductManagement',
        component: () => import('../views/admin/ProductManagement.vue'),
        meta: { title: '管理后台 - 商品管理' }
      },
      {
        path: 'categories',
        name: 'CategoryManagement',
        component: () => import('../views/admin/CategoryManagement.vue'),
        meta: { title: '管理后台 - 分类管理' }
      },
      {
        path: 'audit',
        name: 'AuditManagement',
        component: () => import('../views/admin/AuditManagement.vue'),
        meta: { title: '管理后台 - 审核管理' }
      },
      {
        path: 'logs',
        name: 'SystemLogs',
        component: () => import('../views/admin/SystemLogs.vue'),
        meta: { title: '管理后台 - 系统日志' }
      },
      {
        path: 'orders',
        name: 'AdminOrders',
        component: () => import('../views/admin/OrderManagement.vue'),
        meta: { title: '管理后台 - 订单管理' }
      },
      {
        path: 'reviews',
        name: 'AdminReviews',
        component: () => import('../views/admin/ReviewManagement.vue'),
        meta: { title: '管理后台 - 评价管理' }
      },
      {
        path: 'announcements',
        name: 'AdminAnnouncements',
        component: () => import('../views/admin/AnnouncementManagement.vue'),
        meta: { title: '管理后台 - 公告管理' }
      },
      {
        path: 'reports',
        name: 'AdminReports',
        component: () => import('../views/admin/ReportAppealManagement.vue'),
        meta: { title: '管理后台 - 举报申诉' }
      },
      {
        path: 'banners',
        name: 'AdminBanners',
        component: () => import('../views/admin/BannerManagement.vue'),
        meta: { title: '管理后台 - Banner管理' }
      }
    ]
  },
  {
    path: '/publish',
    name: 'PublishProduct',
    component: () => import('../views/product/PublishProduct.vue'),
    meta: { title: '发布商品', requiresAuth: true }
  },
  {
    path: '/edit/:id',
    name: 'EditProduct',
    component: () => import('../views/product/EditProduct.vue'),
    meta: { title: '编辑商品', requiresAuth: true }
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('../views/Categories.vue'),
    meta: { title: '商品分类' }
  },
  {
    path: '/category/:id',
    name: 'CategoryProducts',
    component: () => import('../views/CategoryProducts.vue'),
    meta: { title: '分类商品' }
  },
  {
    path: '/search',
    name: 'Search',
    component: () => import('../views/Search.vue'),
    meta: { title: '搜索结果' }
  },
  {
    path: '/user/:id',
    name: 'UserProfile',
    component: () => import('../views/user/Profile.vue'),
    meta: { title: '用户主页' }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/user/Profile.vue'),
    meta: { title: '个人中心', requiresAuth: true }
  },
  {
    path: '/my-products',
    name: 'MyProducts',
    component: () => import('../views/user/MyProducts.vue'),
    meta: { title: '我的商品', requiresAuth: true }
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('../views/user/Favorites.vue'),
    meta: { title: '我的收藏', requiresAuth: true }
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/user/History.vue'),
    meta: { title: '浏览历史', requiresAuth: true }
  },
  {
    path: '/cart',
    name: 'Cart',
    component: () => import('../views/user/Cart.vue'),
    meta: { title: '购物车', requiresAuth: true }
  },
  {
    path: '/orders',
    name: 'Orders',
    component: () => import('../views/user/Orders.vue'),
    meta: { title: '订单管理', requiresAuth: true }
  },
  {
    path: '/messages',
    name: 'Messages',
    component: () => import('../views/Messages.vue'),
    meta: { title: '消息中心', requiresAuth: true }
  },
  {
    path: '/chat/:userId?',
    name: 'Chat',
    component: () => import('../views/Chat.vue'),
    meta: { title: '聊天', requiresAuth: true }
  },
  {
    path: '/locations',
    name: 'Locations',
    component: () => import('../views/Locations.vue'),
    meta: { title: '交易地点' }
  },
  {
    path: '/announcements',
    name: 'Announcements',
    component: () => import('../views/Announcements.vue'),
    meta: { title: '平台公告' }
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/About.vue'),
    meta: { title: '关于我们' }
  },
  {
    path: '/terms',
    name: 'Terms',
    component: () => import('../views/Terms.vue'),
    meta: { title: '使用条款' }
  },
  {
    path: '/privacy',
    name: 'Privacy',
    component: () => import('../views/Privacy.vue'),
    meta: { title: '隐私政策' }
  },
  {
    path: '/contact',
    name: 'Contact',
    component: () => import('../views/Contact.vue'),
    meta: { title: '联系我们' }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: () => import('../views/NotFound.vue'),
    meta: { title: '页面未找到' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  }
})

// 全局前置守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 校园二手交易系统` : '校园二手交易系统'
  
  const userStore = useUserStore()
  
  // 1. 如果去往登录/注册页，且已登录，强制去首页
  if (userStore.isLoggedIn && (to.path === '/login' || to.path === '/register')) {
    return next({ path: '/', replace: true })
  }

  // 2. 如果去往需要权限的页面
  if (to.meta.requiresAuth) {
    if (!userStore.isLoggedIn) {
      // 未登录，去登录页
      return next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    }
    
    // 已登录，检查管理员权限
    if (to.meta.requiresAdmin && userStore.userInfo?.role !== 'admin') {
      return next('/403')
    }
    
    // 权限满足，放行
    return next()
  }
  
  // 3. 其他情况（不需要权限的页面），放行
  next()
})

export default router
