<template>
  <div class="home-container">
    <!-- 轮播图 -->
    <div class="banner-section">
      <el-carousel
        :interval="5000"
        height="400px"
        class="banner-carousel"
        arrow="always"
        :autoplay="true"
      >
        <el-carousel-item v-for="item in banners" :key="item.id">
          <div class="banner-slide" :style="{ background: item.bg_color || item.bg }">
            <div class="banner-decor">
              <div class="decor-circle decor-circle-1"></div>
              <div class="decor-circle decor-circle-2"></div>
              <div class="decor-circle decor-circle-3"></div>
            </div>
            <div class="banner-text">
              <span class="banner-tag">{{ item.tag }}</span>
              <h2 class="banner-title">{{ item.title }}</h2>
              <p class="banner-description">{{ item.description }}</p>
              <router-link :to="item.link || '/'" class="banner-button">
                立即查看
                <el-icon class="button-icon"><ArrowRight /></el-icon>
              </router-link>
            </div>
            <div class="banner-emoji">{{ item.emoji }}</div>
          </div>
        </el-carousel-item>
      </el-carousel>
    </div>
    
    <!-- 搜索框 -->
    <div class="home-search-section">
      <div class="search-container">
        <el-input
          v-model="searchQuery"
          placeholder="搜索你想要的商品..."
          :prefix-icon="Search"
          @keyup.enter="handleSearch"
          class="home-search-input"
        >
          <template #append>
            <el-button type="primary" @click="handleSearch" class="home-search-button">
              搜索
            </el-button>
          </template>
        </el-input>
        <div class="hot-searches">
          <span class="hot-searches-title">热门搜索：</span>
          <router-link
            v-for="keyword in hotKeywords"
            :key="keyword"
            :to="`/search?keyword=${keyword}`"
            class="hot-keyword"
          >
            {{ keyword }}
          </router-link>
        </div>
      </div>
    </div>

    <!-- 平台公告 -->
    <div class="announcement-section" v-if="announcements.length > 0">
      <div class="announcement-bar">
        <div class="announcement-icon">
          <el-icon><Bell /></el-icon>
          <span>公告</span>
        </div>
        <div class="announcement-content">
          <el-carousel height="32px" direction="vertical" :autoplay="true" :interval="4000" indicator-position="none">
            <el-carousel-item v-for="ann in announcements" :key="ann.id">
              <div class="announcement-item" @click="showAnnouncementDetail(ann)">
                <el-tag v-if="ann.priority === 'urgent'" type="danger" size="small">紧急</el-tag>
                <el-tag v-else-if="ann.priority === 'high'" type="warning" size="small">重要</el-tag>
                <span class="announcement-title">{{ ann.title }}</span>
                <span class="announcement-time">{{ formatTime(ann.publish_time) }}</span>
              </div>
            </el-carousel-item>
          </el-carousel>
        </div>
        <el-button type="primary" link @click="showAllAnnouncements">查看全部</el-button>
      </div>
    </div>

    <!-- 分类导航 -->
    <div class="categories-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><Menu /></el-icon>
          商品分类
        </h2>
        <router-link to="/products" class="more-link">查看全部 →</router-link>
      </div>
      <div class="categories-grid">
        <router-link 
          v-for="category in categories" 
          :key="category.id" 
          :to="`/category/${category.id}`"
          class="category-item"
          :class="{ 'featured': category.id === 1 }"
        >
          <div class="category-image-wrapper">
            <img :src="category.image" :alt="category.name" class="category-img" />
            <div class="category-icon-overlay" :style="{ backgroundColor: category.color || 'var(--primary-color)' }">
              <el-icon><component :is="getCategoryIcon(category.id)" /></el-icon>
            </div>
          </div>
          <span class="category-name">{{ category.name }}</span>
          <span class="category-count">{{ category.productCount }}件商品</span>
          <div class="category-badge" v-if="category.isNew">新品</div>
        </router-link>
      </div>
    </div>
    
    <!-- 热门商品 -->
    <div class="hot-products-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><Star /></el-icon>
          热门商品
        </h2>
        <router-link to="/products?sort=popular" class="more-link">查看更多 →</router-link>
      </div>
      <div class="products-grid">
        <product-card 
          v-for="product in hotProducts" 
          :key="product.id" 
          :product="{...product, isFeatured: true}"
        />
      </div>
    </div>

    <!-- 猜你喜欢（个性化推荐） -->
    <div class="recommend-section" v-if="recommendProducts.length > 0">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><MagicStick /></el-icon>
          猜你喜欢
        </h2>
        <div class="recommend-actions">
          <span class="recommend-tag">基于你的浏览偏好</span>
          <el-button
            type="primary"
            link
            :loading="recommendLoading"
            @click="handleRefreshRecommendations"
          >
            换一批
          </el-button>
        </div>
      </div>
      <div class="products-grid">
        <product-card
          v-for="product in recommendProducts"
          :key="'rec-' + product.id"
          :product="product"
        />
      </div>
    </div>

    <!-- 最新上架 -->
    <div class="new-products-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><Timer /></el-icon>
          最新上架
        </h2>
        <router-link to="/products?sort=latest" class="more-link">查看更多 →</router-link>
      </div>
      <div class="products-grid">
        <product-card
          v-for="product in newProducts"
          :key="product.id"
          :product="product"
        />
      </div>
    </div>

    <!-- 交易地点推荐 -->
    <div class="locations-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><Location /></el-icon>
          推荐交易地点
        </h2>
        <router-link to="/locations" class="more-link">查看更多 →</router-link>
      </div>
      <div class="locations-grid">
        <router-link
          v-for="location in locations"
          :key="location.id"
          :to="`/products?location=${encodeURIComponent(location.name)}`"
          class="location-item"
        >
          <div class="location-image">
            <img
              :src="location.image || defaultLocationImages[location.name] || defaultLocationImage"
              :alt="location.name"
              loading="lazy"
            />
            <div class="location-overlay">
              <div class="location-actions">
                <span class="action-item">{{ location.usedCount }}次交易</span>
                <el-icon class="action-icon"><ArrowRight /></el-icon>
              </div>
            </div>
          </div>
          <div class="location-info">
            <h3 class="location-name">{{ location.name }}</h3>
            <p class="location-description">{{ location.description }}</p>
            <div class="location-stats">
              <span class="location-rating">
                <el-icon class="rating-icon"><Star /></el-icon>
                <span>{{ (location.rating || 5.0).toFixed(1) }}</span>
              </span>
              <span class="location-distance">{{ location.distance || '0m' }}</span>
            </div>
          </div>
        </router-link>
      </div>
    </div>
    
    <!-- 平台优势 -->
    <div class="advantages-section">
      <div class="advantages-grid">
        <div class="advantage-item">
          <div class="advantage-icon">
            <el-icon class="icon"><Star /></el-icon>
          </div>
          <h3 class="advantage-title">安全交易</h3>
          <p class="advantage-description">平台担保交易，保障资金安全</p>
        </div>
        <div class="advantage-item">
          <div class="advantage-icon">
            <el-icon class="icon"><Location /></el-icon>
          </div>
          <h3 class="advantage-title">便捷配送</h3>
          <p class="advantage-description">校内交易点，方便快捷</p>
        </div>
        <div class="advantage-item">
          <div class="advantage-icon">
            <el-icon class="icon"><Goods /></el-icon>
          </div>
          <h3 class="advantage-title">价格实惠</h3>
          <p class="advantage-description">校内二手，价格更优惠</p>
        </div>
        <div class="advantage-item">
          <div class="advantage-icon">
            <el-icon class="icon"><ChatDotRound /></el-icon>
          </div>
          <h3 class="advantage-title">优质服务</h3>
          <p class="advantage-description">7x24小时客服支持</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import {
  Search,
  Menu,
  Timer,
  Location,
  ArrowRight,
  Goods,
  Document,
  Position,
  House,
  Suitcase,
  More,
  Star,
  ChatDotRound,
  MagicStick,
  Bell
} from '@element-plus/icons-vue'
import ProductCard from '../components/ProductCard.vue'
import productAPI from '../services/productAPI'
import categoryAPI from '../services/categoryAPI'
import locationAPI from '../services/locationAPI'
import recommendAPI from '../services/recommendAPI'
import announcementAPI from '../services/announcementAPI'
import bannerAPI from '../services/bannerAPI'
import { ElMessageBox } from 'element-plus'

const router = useRouter()
const userStore = useUserStore()
const searchQuery = ref('')
const hotKeywords = ref(['iPhone', 'MacBook', 'AirPods', '教材', '运动装备'])

const banners = ref([])

const defaultBanners = [
  {
    id: 1,
    tag: '限时活动',
    title: '开学季大促',
    description: '全场二手教材8折起，数码产品满减优惠',
    bg_color: 'linear-gradient(135deg, #2f3e24 0%, #1c2615 100%)',
    emoji: '📚',
    link: '/products?keyword=教材'
  },
  {
    id: 2,
    tag: '热门专区',
    title: '数码产品专区',
    description: '高品质二手数码，安全交易有保障',
    bg_color: 'linear-gradient(135deg, #3a3022 0%, #241d16 100%)',
    emoji: '💻',
    link: '/products?category=1'
  },
  {
    id: 3,
    tag: '精选推荐',
    title: '运动装备特惠',
    description: '专业运动装备，性价比之选',
    bg_color: 'linear-gradient(135deg, #314228 0%, #1d2a17 100%)',
    emoji: '⚽',
    link: '/products?category=3'
  }
]

const categories = ref([])

const defaultCategoryImages = {
  '数码产品': 'https://images.unsplash.com/photo-1498049794561-7780e7231661?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
  '图书教材': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
  '运动装备': 'https://images.unsplash.com/photo-1517836357463-d25dfeac3438?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
  '生活用品': 'https://images.unsplash.com/photo-1583947215259-38e31be8751f?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
  '服装鞋包': 'https://images.unsplash.com/photo-1489980557514-251d61e3eeb6?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
  '其他物品': 'https://images.unsplash.com/photo-1516321497487-e288fb19713f?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
}

const defaultCategoryColors = {
  '数码产品': 'var(--primary-color)',
  '图书教材': 'var(--success-color)',
  '运动装备': 'var(--warning-color)',
  '生活用品': 'var(--danger-color)',
  '服装鞋包': 'var(--text-tertiary)',
  '其他物品': 'var(--primary-color)'
}

const hotProducts = ref([])
const newProducts = ref([])
const recommendProducts = ref([])
const recommendPool = ref([])
const recommendCursor = ref(0)
const recommendLoading = ref(false)
const locations = ref([])
const announcements = ref([])

const defaultLocationImages = {
  '图书馆': 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=500&q=60',
  '食堂门口': 'https://images.unsplash.com/photo-1567521464027-f127ff144326?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
  '教学楼': 'https://images.unsplash.com/photo-1562774053-701939374585?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
  '操场': 'https://images.unsplash.com/photo-1587280508204-ad3ef5fe1240?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
  '宿舍楼': 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60'
}
const defaultLocationImage = 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=500&q=60'

const RECOMMEND_BATCH_SIZE = 8

const handleSearch = () => {
  if (searchQuery.value.trim()) {
    router.push({ path: '/search', query: { keyword: searchQuery.value } })
  }
}

const getCategoryIcon = (id) => {
  const icons = {
    1: Goods,
    2: Document,
    3: Position,
    4: House,
    5: Suitcase,
    6: More
  }
  return icons[id] || Goods
}

const pickRecommendBatch = (reset = false) => {
  const pool = recommendPool.value
  if (!pool.length) {
    recommendProducts.value = []
    recommendCursor.value = 0
    return
  }

  if (pool.length <= RECOMMEND_BATCH_SIZE) {
    recommendProducts.value = [...pool]
    recommendCursor.value = 0
    return
  }

  const start = reset ? 0 : recommendCursor.value
  const end = start + RECOMMEND_BATCH_SIZE
  if (end <= pool.length) {
    recommendProducts.value = pool.slice(start, end)
  } else {
    recommendProducts.value = [
      ...pool.slice(start),
      ...pool.slice(0, end - pool.length)
    ]
  }
  recommendCursor.value = end % pool.length
}

const loadRecommendations = async (forceRefresh = false) => {
  if (!userStore.isLoggedIn) {
    recommendPool.value = []
    recommendProducts.value = []
    recommendCursor.value = 0
    return
  }

  recommendLoading.value = true
  try {
    const response = await recommendAPI.getPersonalRecommendations(60, { forceRefresh })
    recommendPool.value = response.data.products || []
    pickRecommendBatch(true)
  } catch (error) {
    console.error('获取推荐商品失败:', error)
    recommendPool.value = []
    recommendProducts.value = []
    recommendCursor.value = 0
  } finally {
    recommendLoading.value = false
  }
}

const handleRefreshRecommendations = async () => {
  if (recommendLoading.value) return

  const pool = recommendPool.value
  if (pool.length > RECOMMEND_BATCH_SIZE) {
    // 检查游标是否已经绕回起始位置（说明已经轮完一圈）
    const nextEnd = recommendCursor.value + RECOMMEND_BATCH_SIZE
    if (nextEnd > pool.length && recommendCursor.value !== 0) {
      // 池子快轮完了，从服务器重新获取（强制刷新缓存）
      await loadRecommendations(true)
      return
    }
    pickRecommendBatch(false)
    return
  }

  // 池子太小，从服务器重新获取
  await loadRecommendations(true)
}

// 公告相关方法
const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  const now = new Date()
  const diff = now - date
  if (diff < 86400000) return '今天'
  if (diff < 172800000) return '昨天'
  return `${date.getMonth() + 1}/${date.getDate()}`
}

const showAnnouncementDetail = (ann) => {
  ElMessageBox.alert(ann.content, ann.title, {
    confirmButtonText: '知道了',
    dangerouslyUseHTMLString: false
  })
}

const showAllAnnouncements = () => {
  router.push('/announcements')
}

onMounted(async () => {
  // 获取Banner
  try {
    const response = await bannerAPI.getBanners()
    const fetchedBanners = response.data.banners || []
    banners.value = fetchedBanners.length > 0 ? fetchedBanners : defaultBanners
  } catch (error) {
    console.error('获取Banner失败:', error)
    banners.value = defaultBanners
  }

  // 获取公告
  try {
    const response = await announcementAPI.getLatestAnnouncements(5)
    announcements.value = response.data.announcements || []
  } catch (error) {
    console.error('获取公告失败:', error)
  }

  // 获取分类数据（含真实商品数量）
  try {
    const response = await categoryAPI.getCategories()
    const rawCats = response.data || []
    categories.value = rawCats.map(cat => ({
      ...cat,
      image: defaultCategoryImages[cat.name] || defaultCategoryImages['其他物品'],
      color: defaultCategoryColors[cat.name] || 'var(--primary-color)'
    }))
  } catch (error) {
    console.error('获取分类失败:', error)
  }

  // 获取热门商品
  try {
    const response = await productAPI.getProducts({ sort: 'popular', limit: 4 })
    hotProducts.value = response.data.products || []
  } catch (error) {
    console.error('获取热门商品失败:', error)
    hotProducts.value = [
      {
        id: '1',
        title: 'iPhone 13 Pro',
        price: 4999,
        images: ['https://images.unsplash.com/photo-1632661674596-df8be070a5c5?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
        location: '图书馆',
        created_at: '2024-01-10T10:00:00',
        views: 125,
        favorites: 32,
        chat_count: 15,
        seller_name: '小明',
        user_id: 1
      },
      {
        id: '2',
        title: 'MacBook Air M1',
        price: 6999,
        images: ['https://images.unsplash.com/photo-1611186871348-b1ec696e5237?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
        location: '食堂门口',
        created_at: '2024-01-09T14:30:00',
        views: 89,
        favorites: 25,
        chat_count: 10,
        seller_name: '小红',
        user_id: 2
      },
      {
        id: '3',
        title: 'AirPods Pro',
        price: 999,
        images: ['https://images.unsplash.com/photo-1588423770574-9102111d41e4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
        location: '教学楼',
        created_at: '2024-01-08T09:15:00',
        views: 203,
        favorites: 45,
        chat_count: 28,
        seller_name: '小刚',
        user_id: 3
      }
    ]
  }
  
  // 获取最新商品
  try {
    const response = await productAPI.getProducts({ sort: 'latest', limit: 8 })
    newProducts.value = response.data.products || []
  } catch (error) {
    console.error('获取最新商品失败:', error)
    newProducts.value = [
      {
        id: '7',
        title: 'AirPods 2',
        price: 599,
        images: ['https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
        location: '食堂门口',
        created_at: '2024-01-10T15:20:00',
        views: 56,
        favorites: 12,
        seller_name: '小王',
        user_id: 7
      },
      {
        id: '8',
        title: 'MacBook Pro 14',
        price: 8999,
        images: ['https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
        location: '教学楼',
        created_at: '2024-01-10T14:10:00',
        views: 34,
        favorites: 8,
        seller_name: '小张',
        user_id: 8
      },
      {
        id: '9',
        title: 'iPhone 14',
        price: 5999,
        images: ['https://images.unsplash.com/photo-1663499482523-1c0c1bae4ce1?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
        location: '操场',
        created_at: '2024-01-10T13:00:00',
        views: 98,
        favorites: 23,
        seller_name: '小刘',
        user_id: 9
      },
      {
        id: '10',
        title: 'iPad Air 5',
        price: 3999,
        images: ['https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
        location: '宿舍楼',
        created_at: '2024-01-10T11:45:00',
        views: 45,
        favorites: 15,
        seller_name: '小陈',
        user_id: 10
      },
      {
        id: '11',
        title: 'Apple Watch SE',
        price: 1299,
        images: ['https://images.unsplash.com/photo-1546868871-7041f2a55e12?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
        location: '图书馆',
        created_at: '2024-01-10T10:30:00',
        views: 67,
        favorites: 14,
        seller_name: '小吴',
        user_id: 11
      },
      {
        id: '12',
        title: 'iPhone 13',
        price: 4499,
        images: ['https://images.unsplash.com/photo-1632661674241-5828f04a6741?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'],
        location: '食堂门口',
        created_at: '2024-01-10T09:15:00',
        views: 89,
        favorites: 21,
        seller_name: '小郑',
        user_id: 12
      }
    ]
  }

  // 获取个性化推荐（登录用户）
  await loadRecommendations(false)

  // 获取交易地点
  try {
    const response = await locationAPI.getLocations()
    locations.value = response.data.locations || []
  } catch (error) {
    console.error('获取交易地点失败:', error)
    locations.value = [
      {
        id: 1,
        name: '图书馆',
        description: '图书馆正门，环境安静，安全可靠',
        image: 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=500&q=60',
        usedCount: 1256,
        rating: 4.8,
        distance: '50m'
      },
      {
        id: 2,
        name: '食堂门口',
        description: '食堂正门，人流量大，交易方便',
        image: 'https://images.unsplash.com/photo-1567521464027-f127ff144326?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
        usedCount: 2341,
        rating: 4.6,
        distance: '100m'
      },
      {
        id: 3,
        name: '教学楼',
        description: '教学楼大厅，环境舒适，适合交易',
        image: 'https://images.unsplash.com/photo-1562774053-701939374585?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
        usedCount: 987,
        rating: 4.9,
        distance: '80m'
      },
      {
        id: 4,
        name: '操场',
        description: '操场看台，视野开阔，安全交易',
        image: 'https://images.unsplash.com/photo-1587280508204-ad3ef5fe1240?ixlib=rb-1.2.1&auto=format&fit=crop&w=500&q=60',
        usedCount: 765,
        rating: 4.5,
        distance: '150m'
      }
    ]
  }
})
</script>

<style scoped>
.home-container {
  max-width: var(--container-width);
  margin: 0 auto;
  padding: 0 var(--container-padding);
}

/* 轮播图样式 */
.banner-section {
  margin-bottom: var(--spacing-2xl);
}

.banner-carousel {
  border-radius: var(--border-radius-xl);
  overflow: hidden;
  box-shadow: var(--shadow-lg);
}

.banner-slide {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 80px;
  position: relative;
  overflow: hidden;
}

.banner-decor {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
}

.decor-circle {
  position: absolute;
  border-radius: 50%;
  background: var(--white-alpha-10);
}

.decor-circle-1 {
  width: 300px;
  height: 300px;
  top: -80px;
  right: -60px;
}

.decor-circle-2 {
  width: 200px;
  height: 200px;
  bottom: -60px;
  left: -40px;
}

.decor-circle-3 {
  width: 120px;
  height: 120px;
  top: 50%;
  right: 30%;
  background: var(--white-alpha-06);
}

.banner-text {
  position: relative;
  z-index: 2;
  color: white;
  display: flex;
  flex-direction: column;
  gap: var(--spacing-md);
  max-width: 500px;
}

.banner-tag {
  display: inline-block;
  background: var(--white-alpha-20);
  backdrop-filter: blur(4px);
  padding: 4px 14px;
  border-radius: 20px;
  font-size: var(--font-size-xs);
  font-weight: 500;
  width: fit-content;
}

.recommend-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.banner-title {
  font-size: 32px;
  font-weight: bold;
  margin: 0;
  line-height: 1.2;
}

.banner-description {
  font-size: var(--font-size-md);
  margin: 0;
  opacity: 0.9;
  line-height: 1.6;
}

.banner-button {
  display: inline-flex;
  align-items: center;
  gap: var(--spacing-xs);
  background-color: var(--white-alpha-20);
  backdrop-filter: blur(4px);
  color: white;
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--border-radius-md);
  text-decoration: none;
  font-weight: 500;
  transition: all var(--transition-normal);
  width: fit-content;
  border: 1px solid var(--white-alpha-30);
}

.banner-button:hover {
  background-color: var(--white-alpha-35);
  transform: translateY(-2px);
  color: white;
}

.button-icon {
  font-size: var(--font-size-sm);
}

.banner-emoji {
  font-size: 120px;
  position: relative;
  z-index: 2;
  filter: drop-shadow(0 4px 12px var(--black-alpha-20));
  line-height: 1;
}

/* 搜索框样式 */
.home-search-section {
  margin-bottom: var(--spacing-lg);
}

/* 公告栏样式 */
.announcement-section {
  margin-bottom: var(--spacing-2xl);
}

.announcement-bar {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  background: var(--bg-primary);
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-secondary);
  box-shadow: var(--shadow-sm);
}

.announcement-icon {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  color: var(--primary-color);
  font-weight: 500;
  white-space: nowrap;
}

.announcement-icon .el-icon {
  font-size: 18px;
}

.announcement-content {
  flex: 1;
  overflow: hidden;
}

.announcement-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  cursor: pointer;
  height: 32px;
  line-height: 32px;
}

.announcement-item:hover .announcement-title {
  color: var(--primary-color);
}

.announcement-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--text-primary);
  transition: color var(--transition-fast);
}

.announcement-time {
  color: var(--text-tertiary);
  font-size: var(--font-size-xs);
  white-space: nowrap;
}

:deep(.home-search-input .el-input__inner) {
  color: var(--text-primary) !important;
  background-color: transparent !important;
}

.search-container {
  background: var(--bg-primary) !important;
  padding: var(--spacing-xl);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-md);
  border: 1px solid var(--border-secondary);
}

.home-search-input {
  border-radius: var(--border-radius-lg);
  font-size: var(--font-size-md);
}

:deep(.home-search-input .el-input__wrapper) {
  height: 60px;
  display: flex;
  align-items: center;
  padding: 0 16px;
  border-radius: var(--border-radius-lg) 0 0 var(--border-radius-lg);
  background-color: var(--bg-input) !important;
  box-shadow: none !important;
  border: 1px solid var(--border-primary) !important;
  border-right: none !important;
  outline: none !important;
}

:deep(.home-search-input .el-input__prefix) {
  display: flex;
  align-items: center;
}

:deep(.home-search-input .el-input-group) {
  box-shadow: none !important;
  background-color: transparent !important;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
}

:deep(.home-search-input .el-input-group__append) {
  background-color: var(--primary-color) !important;
  border: 1px solid var(--primary-color) !important;
  border-left: none !important;
  padding: 0;
  border-radius: 0 var(--border-radius-lg) var(--border-radius-lg) 0;
  overflow: hidden;
  box-shadow: none !important;
}

.home-search-button {
  height: 60px;
  border: none;
  border-radius: 0;
  font-size: var(--font-size-lg);
  padding: 0 var(--spacing-xl);
  color: white !important;
  background-color: var(--primary-color);
  width: 120px;
  margin: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hot-searches {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  margin-top: var(--spacing-md);
  flex-wrap: wrap;
}

.hot-searches-title {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  flex-shrink: 0;
}

.hot-keyword {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  text-decoration: none;
  padding: var(--spacing-xs) var(--spacing-sm);
  background-color: var(--bg-quaternary);
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
}

.hot-keyword:hover {
  background-color: var(--primary-color);
  color: white;
}

/* 分类样式 */
.categories-section {
  margin-bottom: var(--spacing-2xl);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-xl);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-xl);
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.section-icon {
  font-size: var(--font-size-lg);
  color: var(--primary-color);
}

.more-link {
  color: var(--primary-color);
  text-decoration: none;
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.more-link:hover {
  color: var(--primary-hover);
  transform: translateX(3px);
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--spacing-xl);
}

.category-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--spacing-xl);
  background-color: var(--bg-primary) !important;
  border-radius: var(--border-radius-lg);
  text-decoration: none;
  color: var(--text-primary);
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
  position: relative;
  overflow: hidden;
  border: 1px solid var(--border-secondary);
}

.category-item:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.category-item.featured {
  background: linear-gradient(135deg, var(--primary-alpha-05), var(--primary-alpha-10));
  border: 1px solid var(--primary-color);
}

.category-image-wrapper {
  position: relative;
  width: 100%;
  padding-top: 100%;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  margin-bottom: var(--spacing-md);
}

.category-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-normal);
}

.category-icon-overlay {
  position: absolute;
  bottom: 0;
  right: 0;
  width: 40px;
  height: 40px;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  border-top-left-radius: var(--border-radius-lg);
  z-index: 2;
  box-shadow: var(--shadow-sm);
}

.category-item:hover .category-img {
  transform: scale(1.1);
}

.category-name {
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
  font-size: var(--font-size-md);
  text-align: center;
}

.category-count {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.category-badge {
  position: absolute;
  top: var(--spacing-sm);
  right: var(--spacing-sm);
  background: var(--danger-color);
  color: white;
  padding: 2px 8px;
  border-radius: var(--border-radius-md);
  font-size: 10px;
  font-weight: 500;
}

/* 商品区域样式 */
.hot-products-section,
.new-products-section,
.recommend-section {
  margin-bottom: var(--spacing-2xl);
  background: var(--bg-primary);
  border-radius: var(--border-radius-xl);
  padding: var(--spacing-xl);
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-secondary);
}

/* 热门商品 - 橙色主题 */
.hot-products-section {
  border-top: 3px solid var(--warning-color);
}

.hot-products-section .section-icon {
  color: var(--warning-color);
}

.hot-products-section .section-title {
  color: var(--text-primary);
}

.hot-products-section .more-link {
  color: var(--warning-color);
}

.hot-products-section .more-link:hover {
  color: var(--warning-color);
}

/* 猜你喜欢 - 紫色主题 */
.recommend-section {
  border-top: 3px solid var(--primary-color);
}

.recommend-section .section-icon {
  color: var(--primary-color);
}

.recommend-tag {
  font-size: var(--font-size-xs);
  color: var(--primary-color);
  background: var(--primary-alpha-10);
  padding: 4px 12px;
  border-radius: 20px;
}

/* 最新上架 - 绿色主题 */
.new-products-section {
  border-top: 3px solid var(--success-color);
}

.new-products-section .section-icon {
  color: var(--success-color);
}

.new-products-section .more-link {
  color: var(--success-color);
}

.new-products-section .more-link:hover {
  color: var(--success-color);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-xl);
}

/* 交易地点样式 */
.locations-section {
  margin-bottom: var(--spacing-2xl);
}

.locations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--spacing-xl);
}

.location-item {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
  text-decoration: none;
  color: var(--text-primary);
}

.location-item:hover {
  transform: translateY(-8px);
  box-shadow: var(--shadow-lg);
}

.location-image {
  position: relative;
  width: 100%;
  padding-top: 75%;
  overflow: hidden;
}

.location-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.location-item:hover .location-image img {
  transform: scale(1.1);
}

.location-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to top, var(--black-alpha-70), transparent);
  opacity: 0;
  transition: opacity var(--transition-normal);
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  padding: var(--spacing-md);
}

.location-item:hover .location-overlay {
  opacity: 1;
}

.location-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  color: white;
  font-size: var(--font-size-sm);
}

.action-item {
  background: var(--white-alpha-20);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--border-radius-md);
  backdrop-filter: blur(5px);
}

.action-icon {
  font-size: var(--font-size-md);
}

.location-info {
  padding: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  gap: var(--spacing-sm);
}

.location-name {
  font-size: var(--font-size-md);
  font-weight: 600;
  margin: 0;
}

.location-description {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0;
  flex: 1;
}

.location-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--spacing-sm);
}

.location-rating {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-xs);
  color: var(--warning-color);
  font-weight: 500;
}

.rating-icon {
  font-size: var(--font-size-sm);
}

.location-distance {
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

/* 平台优势 */
.advantages-section {
  background: linear-gradient(135deg, var(--bg-secondary), var(--bg-quaternary));
  padding: var(--spacing-2xl);
  border-radius: var(--border-radius-xl);
  margin-bottom: var(--spacing-2xl);
}

.advantages-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: var(--spacing-xl);
}

.advantage-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  padding: var(--spacing-xl);
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.advantage-item:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-md);
}

.advantage-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--spacing-md);
  box-shadow: var(--shadow-sm);
}

.advantage-icon .icon {
  font-size: 24px;
}

.advantage-title {
  font-size: var(--font-size-md);
  font-weight: 600;
  margin: 0 0 var(--spacing-xs);
  color: var(--text-primary);
}

.advantage-description {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .banner-carousel {
    height: 350px !important;
  }

  .banner-slide {
    padding: 0 50px;
  }

  .banner-title {
    font-size: var(--font-size-xl);
  }

  .banner-emoji {
    font-size: 90px;
  }
  
  .categories-grid {
    grid-template-columns: repeat(3, 1fr);
  }
  
  .products-grid,
  .locations-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  }
  
  .advantages-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .banner-carousel {
    height: 280px !important;
  }

  .banner-slide {
    padding: 0 30px;
  }

  .banner-title {
    font-size: var(--font-size-lg);
  }

  .banner-description {
    font-size: var(--font-size-sm);
  }

  .banner-emoji {
    font-size: 70px;
  }
  
  .search-container {
    padding: var(--spacing-md);
    bottom: 30px;
  }
  
  .home-search-input {
    height: 44px;
  }
  
  .home-search-button {
    height: 44px;
  }
  
  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: var(--spacing-md);
  }
  
  .category-item {
    padding: var(--spacing-md);
  }
  
  .category-icon {
    width: 60px;
    height: 60px;
    font-size: 24px;
  }
  
  .products-grid,
  .locations-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: var(--spacing-md);
  }

  .hot-products-section,
  .new-products-section,
  .recommend-section {
    padding: var(--spacing-lg);
  }
  
  .location-info {
    padding: var(--spacing-md);
  }
  
  .advantages-grid {
    grid-template-columns: 1fr;
    gap: var(--spacing-md);
  }
  
  .advantages-section {
    padding: var(--spacing-xl);
  }
}

@media (max-width: 480px) {
  .banner-carousel {
    height: 220px !important;
  }

  .banner-slide {
    padding: 0 20px;
  }

  .banner-tag {
    display: none;
  }

  .banner-title {
    font-size: var(--font-size-md);
  }

  .banner-description {
    display: none;
  }

  .banner-button {
    padding: var(--spacing-xs) var(--spacing-md);
    font-size: var(--font-size-sm);
  }

  .banner-emoji {
    font-size: 50px;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
  
  .hot-searches {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-xs);
  }
  
  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .products-grid,
  .locations-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .hot-products-section,
  .new-products-section,
  .recommend-section {
    padding: var(--spacing-md);
  }

  .advantages-section {
    padding: var(--spacing-md);
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.banner-section,
.home-search-section,
.categories-section,
.hot-products-section,
.new-products-section,
.locations-section,
.advantages-section {
  /* animation: fadeInUp 0.8s ease-out forwards; */
  opacity: 1;
}

.banner-section {
  animation-delay: 0.1s;
}

.home-search-section {
  animation-delay: 0.2s;
}

.categories-section {
  animation-delay: 0.3s;
}

.hot-products-section {
  animation-delay: 0.4s;
}

.new-products-section {
  animation-delay: 0.5s;
}

.locations-section {
  animation-delay: 0.6s;
}

.advantages-section {
  animation-delay: 0.7s;
}

/* 加载动画 */
.loading {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-secondary);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 视觉升级覆盖 */
.home-container {
  max-width: 100%;
  padding: 6px 0 0;
}

.banner-section {
  margin-bottom: 36px;
}

.banner-carousel {
  border-radius: 24px;
  border: 1px solid var(--border-secondary);
  box-shadow: var(--shadow-lg);
}

.banner-slide {
  padding: 0 72px;
  isolation: isolate;
}

.banner-slide::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(105deg, var(--black-alpha-10), var(--black-alpha-35));
  z-index: 1;
}

.banner-text,
.banner-emoji {
  z-index: 2;
}

.banner-tag {
  background: var(--white-alpha-22);
  border: 1px solid var(--white-alpha-34);
  box-shadow: 0 8px 20px var(--black-alpha-20);
}

.banner-title {
  font-size: clamp(28px, 3vw, 42px);
  letter-spacing: -0.02em;
}

.banner-description {
  max-width: 520px;
}

.banner-button {
  border-radius: 999px;
  padding: 10px 20px;
}

.banner-emoji {
  font-size: 108px;
  animation: bannerFloat 4.5s ease-in-out infinite;
}

@keyframes bannerFloat {
  0%,
  100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-8px);
  }
}

.search-container {
  padding: 24px;
  background:
    linear-gradient(170deg, var(--primary-alpha-08), var(--primary-alpha-02)),
    var(--bg-primary) !important;
  border-radius: 20px;
  border: 1px solid var(--border-secondary);
  box-shadow: var(--shadow-md);
}

:deep(.home-search-input .el-input__wrapper) {
  border-radius: 999px 0 0 999px !important;
  min-height: 56px;
}

:deep(.home-search-input .el-input-group__append) {
  border-radius: 0 999px 999px 0 !important;
}

.home-search-button {
  height: 56px;
  background: var(--gradient-primary) !important;
  border: none !important;
}

.hot-keyword {
  border: 1px solid transparent;
  background: var(--primary-alpha-08);
  color: var(--primary-color);
}

.hot-keyword:hover {
  border-color: var(--primary-alpha-20);
  box-shadow: 0 8px 18px var(--primary-alpha-20);
}

.section-header {
  margin-bottom: 20px;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.more-link {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--primary-alpha-08);
  border: 1px solid transparent;
}

.more-link:hover {
  border-color: var(--primary-alpha-24);
  transform: translateX(2px);
}

.categories-grid,
.products-grid,
.locations-grid {
  gap: 20px;
}

.category-item {
  border-radius: 18px;
  padding: 16px;
  box-shadow: var(--shadow-sm);
}

.category-item:hover {
  box-shadow: var(--shadow-md);
}

.category-image-wrapper {
  border-radius: 14px;
}

.category-item.featured {
  background: linear-gradient(150deg, var(--primary-alpha-10), var(--primary-alpha-02));
}

.hot-products-section,
.new-products-section,
.recommend-section {
  border-radius: 20px;
  box-shadow: var(--shadow-sm);
  background: var(--bg-primary);
}

.hot-products-section {
  border-top: 3px solid var(--warning-color);
}

.hot-products-section .section-icon,
.hot-products-section .more-link {
  color: var(--warning-color);
}

.recommend-section {
  border-top: 3px solid var(--primary-color);
}

.recommend-section .section-icon {
  color: var(--primary-color);
}

.recommend-tag {
  color: var(--primary-color);
  background: var(--primary-alpha-10);
}

.new-products-section {
  border-top: 3px solid var(--success-color);
}

.new-products-section .section-icon,
.new-products-section .more-link {
  color: var(--success-color);
}

.location-item {
  border-radius: 18px;
  border: 1px solid var(--border-secondary);
}

.location-item:hover {
  border-color: var(--primary-alpha-20);
}

.location-info {
  padding: 18px;
}

.advantages-section {
  background:
    linear-gradient(145deg, var(--primary-alpha-10), var(--primary-alpha-06)),
    var(--bg-primary);
  border: 1px solid var(--border-secondary);
  box-shadow: var(--shadow-sm);
}

.advantage-item {
  border: 1px solid var(--border-secondary);
  border-radius: 18px;
}

.advantage-icon {
  width: 56px;
  height: 56px;
}

@media (max-width: 1024px) {
  .banner-slide {
    padding: 0 46px;
  }

  .products-grid,
  .locations-grid {
    grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  }
}

@media (max-width: 768px) {
  .banner-slide {
    padding: 0 24px;
  }

  .search-container {
    padding: 16px;
  }

  .hot-products-section,
  .new-products-section,
  .recommend-section,
  .advantages-section {
    padding: 16px;
  }
}

@media (max-width: 480px) {
  .banner-carousel {
    border-radius: 16px;
  }

  .banner-emoji {
    font-size: 46px;
  }

  .section-title {
    font-size: 20px;
  }
}

/* WP-DOS inspired overrides */
.home-container {
  padding-top: 8px;
}

.banner-carousel {
  border-radius: 8px;
  border: 1px solid var(--border-primary);
  box-shadow: none;
}

.banner-slide {
  padding: 0 52px;
}

.banner-slide::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    linear-gradient(var(--bg-overlay), var(--bg-overlay)),
    url('../assets/dos_noise-texture.png');
  background-size: auto, 260px 260px;
  z-index: 1;
}

.banner-slide::after {
  background:
    repeating-linear-gradient(
      180deg,
      var(--primary-alpha-10) 0,
      var(--primary-alpha-10) 1px,
      transparent 1px,
      transparent 3px
    ),
    linear-gradient(105deg, var(--black-alpha-30), var(--black-alpha-60));
}

.banner-decor {
  opacity: 0.3;
}

.banner-text {
  color: var(--text-primary);
}

.banner-tag {
  color: var(--text-primary);
  background: var(--primary-alpha-10);
  border: 1px solid var(--primary-alpha-35);
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.banner-title {
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.banner-description {
  color: var(--text-secondary);
}

.banner-button {
  border-radius: 4px;
  border: 1px solid var(--border-primary);
  color: var(--bg-primary);
  background: var(--gradient-primary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.banner-button:hover {
  transform: none;
  filter: brightness(1.05);
}

.banner-emoji {
  opacity: 1;
  filter: none;
}

.search-container {
  border-radius: 8px;
  border: 1px solid var(--border-primary);
  box-shadow: none;
  background:
    linear-gradient(var(--bg-overlay), var(--bg-overlay)),
    url('../assets/dos_noise-texture.png') !important;
}

:deep(.home-search-input .el-input__wrapper) {
  min-height: 52px;
  border-radius: 4px 0 0 4px !important;
  border: 1px solid var(--border-primary) !important;
}

:deep(.home-search-input .el-input-group__append) {
  border-radius: 0 4px 4px 0 !important;
}

.home-search-button {
  height: 52px;
  width: 110px;
  color: var(--bg-primary) !important;
  letter-spacing: 0.08em;
}

.hot-keyword {
  border-radius: 4px;
  border: 1px solid var(--border-secondary);
  background: var(--bg-input);
  color: var(--text-secondary);
}

.hot-keyword:hover {
  color: var(--bg-primary);
  background: var(--primary-color);
  border-color: var(--primary-color);
  box-shadow: none;
}

.section-title {
  font-size: 18px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.section-icon {
  color: var(--primary-color) !important;
}

.more-link {
  border-radius: 4px;
  border: 1px solid var(--border-primary);
  background: var(--bg-elevated);
  color: var(--text-secondary) !important;
  text-decoration: none;
}

.more-link:hover {
  transform: none;
  border-color: var(--primary-color);
  color: var(--text-primary) !important;
}

.category-item,
.location-item,
.advantage-item {
  border-radius: 6px;
  border: 1px solid var(--border-primary);
  box-shadow: none;
  background: var(--bg-elevated) !important;
}

.category-item:hover,
.location-item:hover,
.advantage-item:hover {
  transform: none;
  border-color: var(--primary-color);
  box-shadow: none;
}

.category-item.featured {
  background: color-mix(in srgb, var(--bg-elevated) 72%, var(--primary-color) 28%) !important;
  border-color: var(--primary-color);
}

.category-icon-overlay {
  border-top-left-radius: 4px;
  box-shadow: none;
}

.hot-products-section,
.new-products-section,
.recommend-section {
  border-radius: 8px;
  border: 1px solid var(--border-primary);
  box-shadow: none;
  background:
    linear-gradient(var(--bg-overlay), var(--bg-overlay)),
    url('../assets/dos_noise-texture.png');
  background-size: auto, 260px 260px;
}

.hot-products-section,
.new-products-section,
.recommend-section {
  border-top: 2px solid var(--primary-color);
}

.hot-products-section .more-link,
.new-products-section .more-link,
.recommend-section .more-link,
.hot-products-section .section-icon,
.new-products-section .section-icon,
.recommend-section .section-icon,
.recommend-tag {
  color: var(--primary-color) !important;
}

.recommend-tag {
  border-radius: 4px;
  border: 1px solid color-mix(in srgb, var(--primary-color) 56%, transparent 44%);
  background: color-mix(in srgb, var(--primary-color) 14%, transparent 86%);
}

.location-overlay {
  background: linear-gradient(to top, var(--black-alpha-80), var(--black-alpha-20), transparent);
}

.action-item {
  border-radius: 4px;
  border: 1px solid var(--primary-alpha-24);
}

.advantages-section {
  border-radius: 8px;
  border: 1px solid var(--border-primary);
  box-shadow: none;
  background:
    linear-gradient(var(--bg-overlay), var(--bg-overlay)),
    url('../assets/dos_noise-texture.png');
}

.advantage-icon {
  border-radius: 4px;
  box-shadow: none;
  color: var(--bg-primary);
  background: var(--gradient-primary);
}

@media (max-width: 768px) {
  .banner-slide {
    padding: 0 24px;
  }

  .home-search-button {
    height: 46px;
  }

  :deep(.home-search-input .el-input__wrapper) {
    min-height: 46px;
  }
}
</style>
