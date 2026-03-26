<template>
  <div class="product-detail-container" v-if="product">
    <!-- 商品基本信息 -->
    <div class="product-basic-section">
      <div class="product-images-section">
        <div class="main-image">
          <img :src="currentImage" :alt="product.title" class="main-img" />
          <div class="image-overlay">
            <div class="image-actions">
              <button class="action-btn zoom-btn" @click="handleImageZoom">
                <el-icon><ZoomIn /></el-icon>
              </button>
            </div>
          </div>
        </div>
        <div class="thumbnail-images" v-if="product.images && product.images.length > 1">
          <div 
            v-for="(image, index) in product.images" 
            :key="index"
            class="thumbnail-item"
            :class="{ active: currentIndex === index }"
            @click="currentIndex = index"
          >
            <img :src="image" :alt="product.title" class="thumbnail-img" />
          </div>
        </div>
      </div>
      
      <!-- 商品信息 -->
      <div class="product-info-section">
        <div class="product-status-badge" v-if="product.status === 'sold'">已售</div>
        <h1 class="product-title">{{ product.title }}</h1>
        <div class="product-price">
          <span class="price-symbol">¥</span>
          <span class="price-value">{{ product.price }}</span>
        </div>
        
        <div class="product-meta">
          <div class="meta-item">
            <el-icon class="meta-icon"><Timer /></el-icon>
            <span class="meta-value">{{ formatTime(product.created_at) }}</span>
          </div>
          <div class="meta-item">
            <el-icon class="meta-icon"><View /></el-icon>
            <span class="meta-value">{{ product.views || 0 }}浏览</span>
          </div>
          <div class="meta-item">
            <el-icon class="meta-icon"><Star /></el-icon>
            <span class="meta-value">{{ product.favorites || 0 }}收藏</span>
          </div>
          <div class="meta-item" v-if="product.quantity">
            <el-icon class="meta-icon"><Box /></el-icon>
            <span class="meta-value">库存 {{ product.quantity }} 件</span>
          </div>
        </div>
        
        <div class="product-location">
          <div class="location-info">
            <el-icon class="location-icon"><Location /></el-icon>
            <span class="location-text">{{ product.location || '未设置' }}</span>
          </div>
        </div>

        <div class="product-condition" v-if="product.condition">
          <div class="condition-info">
            <el-icon class="condition-icon"><Goods /></el-icon>
            <span class="condition-text">成色：{{ product.condition }}</span>
          </div>
        </div>
        
        <div class="product-seller">
          <div class="seller-info">
            <router-link v-if="sellerRoute" :to="sellerRoute" class="seller-link">
              <div class="seller-avatar">
                {{ product.seller?.username?.charAt(0).toUpperCase() || 'U' }}
              </div>
              <div class="seller-details">
                <div class="seller-name">{{ product.seller?.username || '未知用户' }}</div>
                <div class="seller-school">{{ product.seller?.school || product.seller?.school_name || '未知学校' }}</div>
              </div>
            </router-link>
            <div v-else class="seller-link">
              <div class="seller-avatar">U</div>
              <div class="seller-details">
                <div class="seller-name">未知用户</div>
                <div class="seller-school">未知学校</div>
              </div>
            </div>
            <router-link 
              v-if="sellerId && isLoggedIn && sellerId !== userInfo.id"
              :to="`/chat/${sellerId}?username=${encodeURIComponent(product?.seller?.username || '')}`" 
              class="chat-button"
            >
              <el-icon><ChatLineRound /></el-icon>
              联系卖家
            </router-link>
          </div>
        </div>

        <!-- 购买数量选择 (仅当库存>1时显示) -->
        <div class="quantity-selector" v-if="product.quantity > 1 && product.status !== 'sold' && (!isLoggedIn || sellerId !== userInfo.id)">
          <span class="quantity-label">购买数量：</span>
          <el-input-number
            v-model="purchaseQuantity"
            :min="1"
            :max="product.quantity"
            size="large"
            style="width: 150px"
          />
          <span class="quantity-tip">最多 {{ product.quantity }} 件</span>
        </div>

        <div class="product-actions">
          <el-button
            type="success"
            class="action-button buy-button"
            @click="handleBuy"
            :disabled="product.status === 'sold' || (product.quantity && product.quantity <= 0)"
            v-if="!isLoggedIn || sellerId !== userInfo.id"
          >
            <el-icon><ShoppingCart /></el-icon>
            {{ product.status === 'sold' ? '已售出' : (product.quantity && product.quantity <= 0 ? '库存不足' : '立即购买') }}
          </el-button>
          <el-button
            type="warning"
            class="action-button cart-button"
            @click="handleAddToCart"
            :disabled="product.status === 'sold'"
            v-if="!isLoggedIn || sellerId !== userInfo.id"
          >
            <el-icon><ShoppingCart /></el-icon>
            加入购物车
          </el-button>
          <el-button
            type="primary"
            class="action-button chat-button"
            @click="handleContact"
            v-if="!isLoggedIn || sellerId !== userInfo.id"
          >
            <el-icon><ChatLineRound /></el-icon>
            立即联系
          </el-button>
          <el-button 
            class="action-button favorite-button"
            :type="isFavorite ? 'warning' : 'default'"
            @click="handleFavorite"
          >
            <el-icon>
              <StarFilled v-if="isFavorite" />
              <Star v-else />
            </el-icon>
            {{ isFavorite ? '已收藏' : '收藏' }}
          </el-button>
          <el-button 
            class="action-button share-button"
            @click="handleShare"
          >
            <el-icon><Share /></el-icon>
            分享
          </el-button>
        </div>
      </div>
    </div>
    
    <!-- 商品详情 -->
    <div class="product-detail-section">
      <div class="section-tabs">
        <button 
          class="tab-button" 
          :class="{ active: activeTab === 'description' }"
          @click="activeTab = 'description'"
        >
          商品描述
        </button>
        <button 
          class="tab-button" 
          :class="{ active: activeTab === 'trade' }"
          @click="activeTab = 'trade'"
        >
          交易信息
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'seller' }"
          @click="activeTab = 'seller'"
        >
          卖家信息
        </button>
        <button
          class="tab-button"
          :class="{ active: activeTab === 'reviews' }"
          @click="activeTab = 'reviews'"
        >
          商品评价
        </button>
      </div>
      
      <div class="tab-content">
        <div v-if="activeTab === 'description'" class="product-description-section">
          <h2 class="section-title">
            <el-icon class="section-icon"><Document /></el-icon>
            商品描述
          </h2>
          <div class="description-content">
            {{ product.description }}
          </div>
        </div>
        
        <div v-if="activeTab === 'trade'" class="product-trade-info">
          <h3 class="info-title">交易信息</h3>
          <div class="info-item">
            <span class="info-label">交易方式：</span>
            <span class="info-value">线下交易</span>
          </div>
          <div class="info-item">
            <span class="info-label">交易地点：</span>
            <router-link :to="`/search?location=${product.location}`" class="info-value location-link">
              {{ product.location }}
            </router-link>
          </div>
          <div class="info-item">
            <span class="info-label">发布时间：</span>
            <span class="info-value">{{ formatTime(product.created_at) }}</span>
          </div>

          <!-- 安全提示 -->
          <div class="safety-section">
            <SafetyTips />
          </div>

          <!-- 时空匹配 -->
          <div class="time-location-section" v-if="isLoggedIn && sellerId !== userInfo.id">
            <TimeLocationMatch :item-id="productId" />
          </div>
        </div>
        
        <div v-if="activeTab === 'seller'" class="product-seller-info">
          <h3 class="info-title">卖家信息</h3>
          <div class="seller-card">
            <router-link v-if="sellerRoute" :to="sellerRoute" class="seller-card-link">
              <div class="seller-avatar-large">
                {{ product.seller?.username?.charAt(0).toUpperCase() || 'U' }}
              </div>
              <div class="seller-details-large">
                <div class="seller-name-large">{{ product.seller?.username || '未知用户' }}</div>
                <div class="seller-school-large">{{ product.seller?.school || product.seller?.school_name || '未知学校' }}</div>
              </div>
              <el-icon class="view-more-icon"><ArrowRight /></el-icon>
            </router-link>
            <div v-else class="seller-card-link">
              <div class="seller-avatar-large">U</div>
              <div class="seller-details-large">
                <div class="seller-name-large">未知用户</div>
                <div class="seller-school-large">未知学校</div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="activeTab === 'reviews'" class="product-reviews-section">
          <ReviewList :item-id="productId" />
        </div>
      </div>
    </div>
    
    <!-- 相关推荐 -->
    <div class="related-products-section">
      <div class="section-header">
        <h2 class="section-title">
          <el-icon class="section-icon"><Goods /></el-icon>
          相关推荐
        </h2>
        <router-link to="/products" class="more-link">查看更多 →</router-link>
      </div>
      <div class="products-grid">
        <product-card 
          v-for="item in relatedProducts" 
          :key="item.id" 
          :product="item"
        />
      </div>
    </div>
  </div>
  <div class="loading-container" v-else>
    <div class="loading-content">
      <div class="loading-spinner"></div>
      <p class="loading-text">加载中...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  ZoomIn, 
  Timer, 
  View, 
  Star, 
  StarFilled, 
  Location, 
  ChatLineRound, 
  ShoppingCart, 
  Share, 
  Document, 
  ArrowRight,
  Goods
} from '@element-plus/icons-vue'
import ProductCard from '../../components/ProductCard.vue'
import TimeLocationMatch from '../../components/TimeLocationMatch.vue'
import SafetyTips from '../../components/SafetyTips.vue'
import ReviewList from '../../components/ReviewList.vue'
import productAPI from '../../services/productAPI'
import recommendAPI from '../../services/recommendAPI'
import orderAPI from '../../services/orderAPI'
import cartAPI from '../../services/cartAPI'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const productId = computed(() => route.params.id)
const product = ref(null)
const relatedProducts = ref([])
const loading = ref(true)
const currentIndex = ref(0)
const isFavorite = ref(false)
const activeTab = ref('description')
const lastRecordedViewId = ref(null)
const purchaseQuantity = ref(1)

const sellerId = computed(() => {
  return product.value?.seller?.id || product.value?.seller_id || product.value?.user_id
})

const sellerRoute = computed(() => {
  if (!sellerId.value) return null
  return {
    path: `/user/${sellerId.value}`,
    query: {
      name: product.value?.seller?.username || undefined,
      school: product.value?.seller?.school || undefined
    }
  }
})

const currentImage = computed(() => {
  if (product.value?.images && product.value.images.length > 0) {
    return product.value.images[currentIndex.value]
  }
  return 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400"%3E%3Crect fill="%23f0f0f0" width="400" height="400"/%3E%3Ctext fill="%23999" font-family="Arial" font-size="16" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E暂无图片%3C/text%3E%3C/svg%3E'
})

const isLoggedIn = computed(() => userStore.isLoggedIn)
const userInfo = computed(() => userStore.userInfo)

const formatTime = (timeString) => {
  if (!timeString) return ''
  
  const time = new Date(timeString)
  return time.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleFavorite = async () => {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }
  
  try {
    if (isFavorite.value) {
      await productAPI.unfavoriteProduct(productId.value)
      isFavorite.value = false
      // 更新本地收藏数
      if (product.value.favorites) {
        product.value.favorites--
      }
    } else {
      await productAPI.favoriteProduct(productId.value)
      isFavorite.value = true
      // 更新本地收藏数
      product.value.favorites = (product.value.favorites || 0) + 1
    }
  } catch (error) {
    console.error('操作失败:', error)
    // 显示错误提示
  }
}

const handleShare = () => {
  if (navigator.share) {
    // 使用Web Share API
    navigator.share({
      title: product.value.title,
      text: product.value.description,
      url: window.location.href
    }).catch(err => {
      console.error('分享失败:', err)
    })
  } else {
    // 复制链接到剪贴板
    navigator.clipboard.writeText(window.location.href).then(() => {
      // 显示复制成功提示
      console.log('链接已复制到剪贴板')
    }).catch(err => {
      console.error('复制失败:', err)
    })
  }
}

const handleImageZoom = () => {
  console.log('图片放大查看')
}

const handleContact = () => {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }
  router.push(`/chat/${product.value.seller?.id}?username=${encodeURIComponent(product.value.seller?.username || '')}`)
}

const handleBuy = () => {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }

  if (product.value.status === 'sold') {
    ElMessage.warning('该商品已售出')
    return
  }

  const quantity = product.value.quantity > 1 ? purchaseQuantity.value : 1
  const totalPrice = (product.value.price * quantity).toFixed(2)
  const quantityText = quantity > 1 ? ` × ${quantity}件` : ''

  ElMessageBox.confirm(
    `确定要购买「${product.value.title || product.value.name}」${quantityText} (¥${totalPrice}) 吗？`,
    '确认购买',
    { confirmButtonText: '确认购买', cancelButtonText: '取消', type: 'info' }
  ).then(async () => {
    try {
      await orderAPI.createOrder({
        item_id: product.value.id,
        quantity: quantity
      })
      ElMessage.success('下单成功！')

      // 更新本地库存显示
      product.value.quantity = product.value.quantity - quantity
      if (product.value.quantity <= 0) {
        product.value.status = 'sold'
      }

      router.push('/orders')
    } catch (e) {
      ElMessage.error(e?.response?.data?.msg || '下单失败，请稍后重试')
    }
  }).catch(() => {})
}

const handleAddToCart = async () => {
  if (!isLoggedIn.value) {
    router.push('/login')
    return
  }
  if (product.value.status === 'sold') {
    ElMessage.warning('该商品已售出')
    return
  }
  try {
    await cartAPI.addToCart(product.value.id)
    ElMessage.success('已加入购物车')
  } catch (e) {
    const msg = e?.response?.data?.msg || ''
    if (msg.includes('already') || msg.includes('重复') || e?.response?.status === 409) {
      ElMessage.info('该商品已在购物车中')
    } else {
      ElMessage.error(msg || '加入购物车失败')
    }
  }
}

const loadProductDetail = async () => {
  loading.value = true
  try {
    // 获取商品详情
    const response = await productAPI.getProductById(productId.value)
    product.value = response.data
    
    // 记录浏览历史（同一商品只记录一次）
    if (isLoggedIn.value && String(productId.value) !== String(lastRecordedViewId.value)) {
      try {
        await productAPI.recordView(productId.value)
        lastRecordedViewId.value = productId.value
      } catch (error) {
        console.error('记录浏览历史失败:', error)
      }
    }
    
    // 检查是否已收藏
    if (isLoggedIn.value) {
      try {
        const favoritesResponse = await productAPI.getFavorites()
        const favorites = favoritesResponse.data.products || []
        isFavorite.value = favorites.some(item => String(item.id) === String(productId.value))
      } catch (error) {
        console.error('获取收藏列表失败:', error)
        isFavorite.value = false
      }
    }
    
    // 获取相关推荐（优先使用推荐引擎）
    try {
      const recResponse = await recommendAPI.getSimilarItems(productId.value, 6)
      relatedProducts.value = (recResponse.data.products || [])
        .filter(item => String(item.id) !== String(productId.value))
      // 推荐结果不足时用同类别补充
      if (relatedProducts.value.length < 4 && product.value.category_id) {
        const relatedResponse = await productAPI.getProducts({
          category_id: product.value.category_id,
          limit: 6
        })
        const extra = (relatedResponse.data.products || [])
          .filter(item => String(item.id) !== String(productId.value))
        const existIds = new Set(relatedProducts.value.map(i => String(i.id)))
        for (const item of extra) {
          if (!existIds.has(String(item.id))) {
            relatedProducts.value.push(item)
          }
          if (relatedProducts.value.length >= 6) break
        }
      }
    } catch (error) {
      console.error('获取相关商品失败:', error)
      relatedProducts.value = []
    }
  } catch (error) {
    console.error('获取商品详情失败:', error)
    // 使用模拟数据，根据不同的productId显示不同的商品
    const mockProducts = {
      '1': {
        id: '1',
        title: 'iPhone 13 Pro',
        price: 4999,
        images: [
          'https://images.unsplash.com/photo-1632661674596-df8be070a5c5?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '9成新，无划痕，配件齐全，原装充电器，电池健康度95%',
        location: '图书馆',
        created_at: '2024-01-10T10:00:00',
        views: 125,
        favorites: 32,
        seller: {
          id: 1,
          username: '小明',
          school: '清华大学'
        }
      },
      '2': {
        id: '2',
        title: 'MacBook Air M1',
        price: 6999,
        images: [
          'https://images.unsplash.com/photo-1611186871348-b1ec696e5237?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '全新未拆封，官方正品，支持验货，有发票',
        location: '食堂门口',
        created_at: '2024-01-09T14:30:00',
        views: 89,
        favorites: 25,
        seller: {
          id: 2,
          username: '小红',
          school: '北京大学'
        }
      },
      '3': {
        id: '3',
        title: 'AirPods Pro',
        price: 999,
        images: [
          'https://images.unsplash.com/photo-1588423770574-9102111d41e4?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '8成新，功能正常，无损坏，含原装充电盒',
        location: '教学楼',
        created_at: '2024-01-08T09:15:00',
        views: 203,
        favorites: 45,
        seller: {
          id: 3,
          username: '小刚',
          school: '复旦大学'
        }
      },
      '4': {
        id: '4',
        title: 'iPad Pro 12.9',
        price: 5999,
        images: [
          'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '9成新，WiFi版，128GB，带Apple Pencil',
        location: '操场',
        created_at: '2024-01-07T16:45:00',
        views: 67,
        favorites: 18,
        seller: {
          id: 4,
          username: '小丽',
          school: '上海交通大学'
        }
      },
      '5': {
        id: '5',
        title: 'Apple Watch Series 7',
        price: 1999,
        images: [
          'https://images.unsplash.com/photo-1434493907317-a46b53b81822?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '全新，未拆封，45mm，GPS版，黑色',
        location: '宿舍楼',
        created_at: '2024-01-06T11:20:00',
        views: 145,
        favorites: 30,
        seller: {
          id: 5,
          username: '小强',
          school: '浙江大学'
        }
      },
      '6': {
        id: '6',
        title: 'iPhone 12',
        price: 3499,
        images: [
          'https://images.unsplash.com/photo-1611605698335-8b1569810432?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '8成新，有轻微划痕，功能正常，电池健康度85%',
        location: '图书馆',
        created_at: '2024-01-05T13:50:00',
        views: 189,
        favorites: 42,
        seller: {
          id: 6,
          username: '小美',
          school: '南京大学'
        }
      },
      '7': {
        id: '7',
        title: 'AirPods 2',
        price: 599,
        images: [
          'https://images.unsplash.com/photo-1572569511254-d8f925fe2cbb?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '9成新，功能正常，无损坏，含原装充电盒',
        location: '食堂门口',
        created_at: '2024-01-10T15:20:00',
        views: 56,
        favorites: 12,
        seller: {
          id: 7,
          username: '小王',
          school: '武汉大学'
        }
      },
      '8': {
        id: '8',
        title: 'MacBook Pro 14',
        price: 8999,
        images: [
          'https://images.unsplash.com/photo-1517336714731-489689fd1ca8?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '全新未拆封，官方正品，支持验货，有发票',
        location: '教学楼',
        created_at: '2024-01-10T14:10:00',
        views: 34,
        favorites: 8,
        seller: {
          id: 8,
          username: '小张',
          school: '华中科技大学'
        }
      },
      '9': {
        id: '9',
        title: 'iPhone 14',
        price: 5999,
        images: [
          'https://images.unsplash.com/photo-1663499482523-1c0c1bae4ce1?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '9成新，无划痕，配件齐全，原装充电器，电池健康度95%',
        location: '操场',
        created_at: '2024-01-10T13:00:00',
        views: 98,
        favorites: 23,
        seller: {
          id: 9,
          username: '小刘',
          school: '中山大学'
        }
      },
      '10': {
        id: '10',
        title: 'iPad Air 5',
        price: 3999,
        images: [
          'https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '9成新，WiFi版，64GB，无划痕',
        location: '宿舍楼',
        created_at: '2024-01-10T11:45:00',
        views: 45,
        favorites: 15,
        seller: {
          id: 10,
          username: '小陈',
          school: '四川大学'
        }
      },
      '11': {
        id: '11',
        title: 'Apple Watch SE',
        price: 1299,
        images: [
          'https://images.unsplash.com/photo-1546868871-7041f2a55e12?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '全新，未拆封，44mm，GPS版，白色',
        location: '图书馆',
        created_at: '2024-01-10T10:30:00',
        views: 67,
        favorites: 14,
        seller: {
          id: 11,
          username: '小吴',
          school: '南开大学'
        }
      },
      '12': {
        id: '12',
        title: 'iPhone 13',
        price: 4499,
        images: [
          'https://images.unsplash.com/photo-1632661674241-5828f04a6741?ixlib=rb-1.2.1&auto=format&fit=crop&w=800&q=80'
        ],
        description: '8成新，有轻微划痕，功能正常，电池健康度90%',
        location: '食堂门口',
        created_at: '2024-01-10T09:15:00',
        views: 89,
        favorites: 21,
        seller: {
          id: 12,
          username: '小郑',
          school: '天津大学'
        }
      }
    }
    
    // 获取当前商品的模拟数据，如果没有则使用默认商品
    product.value = mockProducts[productId.value] || mockProducts['1']
    
    // 模拟相关推荐，排除当前商品
    const allMockProducts = Object.values(mockProducts)
    relatedProducts.value = allMockProducts
      .filter(item => item.id !== productId.value)
      .slice(0, 6)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  window.scrollTo({ top: 0, behavior: 'auto' })
  loadProductDetail()
})

watch(() => route.params.id, (newId, oldId) => {
  if (route.name === 'ProductDetail' && newId !== oldId) {
    currentIndex.value = 0
    activeTab.value = 'description'
    loadProductDetail()
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
})
</script>

<style scoped>
.product-detail-container {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-xl);
  padding: var(--spacing-lg) 0;
}

/* 商品基本信息 */
.product-basic-section {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--spacing-xl);
  background: var(--bg-primary);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-xl);
  position: relative;
}

/* 商品图片展示 */
.product-images-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
}

.main-image {
  position: relative;
  width: 100%;
  aspect-ratio: 1/1;
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-md);
}

.main-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform var(--transition-slow);
}

.main-image:hover .main-img {
  transform: scale(1.05);
}

.image-overlay {
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
  justify-content: flex-end;
  padding: var(--spacing-lg);
}

.main-image:hover .image-overlay {
  opacity: 1;
}

.image-actions {
  display: flex;
  gap: var(--spacing-sm);
}

.action-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--white-alpha-90);
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all var(--transition-normal);
  font-size: 18px;
  color: var(--text-secondary);
}

.action-btn:hover {
  background: var(--primary-color);
  color: white;
  transform: scale(1.1);
}

.thumbnail-images {
  display: flex;
  gap: var(--spacing-md);
  justify-content: flex-start;
  overflow-x: auto;
  padding-bottom: var(--spacing-sm);
}

.thumbnail-item {
  width: 80px;
  height: 80px;
  border-radius: var(--border-radius-md);
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all var(--transition-normal);
  flex-shrink: 0;
  box-shadow: var(--shadow-sm);
}

.thumbnail-item:hover {
  border-color: var(--primary-color);
  transform: translateY(-2px);
}

.thumbnail-item.active {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 2px var(--primary-alpha-20);
}

.thumbnail-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* 商品信息 */
.product-info-section {
  display: flex;
  flex-direction: column;
  gap: var(--spacing-lg);
  position: relative;
}

/* 购买数量选择器 */
.quantity-selector {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  background: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
  border: 1px solid var(--border-color);
}

.quantity-label {
  font-size: var(--font-size-base);
  font-weight: 500;
  color: var(--text-primary);
}

.quantity-tip {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.product-status-badge {
  position: absolute;
  top: 0;
  right: 0;
  background: linear-gradient(135deg, var(--danger-color), var(--danger-color));
  color: white;
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: 0 var(--border-radius-lg) 0 var(--border-radius-lg);
  font-size: var(--font-size-sm);
  font-weight: 500;
  z-index: 10;
}

.product-title {
  font-size: var(--font-size-2xl);
  font-weight: 600;
  margin: 0;
  line-height: 1.4;
  color: var(--text-primary);
}

.product-price {
  display: flex;
  align-items: baseline;
  gap: 4px;
  margin: var(--spacing-sm) 0;
}

.price-symbol {
  font-size: var(--font-size-lg);
  color: var(--danger-color);
}

.price-value {
  font-size: var(--font-size-3xl);
  font-weight: bold;
  color: var(--danger-color);
}

.product-meta {
  display: flex;
  flex-wrap: wrap;
  gap: var(--spacing-md);
  padding-bottom: var(--spacing-lg);
  border-bottom: 1px solid var(--border-secondary);
}

.meta-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.meta-icon {
  font-size: var(--font-size-md);
  color: var(--text-tertiary);
}

.product-location {
  padding: var(--spacing-md);
  background: var(--bg-quaternary);
  border-radius: var(--border-radius-md);
  margin: var(--spacing-sm) 0;
}

.location-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.location-icon {
  font-size: var(--font-size-md);
  color: var(--primary-color);
}

.product-condition {
  padding: var(--spacing-md);
  background: var(--bg-quaternary);
  border-radius: var(--border-radius-md);
  margin: var(--spacing-sm) 0;
}

.condition-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.condition-icon {
  font-size: var(--font-size-md);
  color: var(--primary-color);
}

.location-text {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-seller {
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--border-secondary);
}

.seller-info {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.seller-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  text-decoration: none;
  color: var(--text-primary);
  transition: all var(--transition-normal);
  flex: 1;
}

.seller-link:hover {
  color: var(--primary-color);
}

.seller-avatar {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-xl);
  font-weight: bold;
  transition: all var(--transition-normal);
  box-shadow: var(--shadow-sm);
}

.seller-link:hover .seller-avatar {
  transform: scale(1.1);
}

.seller-details {
  flex: 1;
}

.seller-name {
  font-size: var(--font-size-md);
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
}

.seller-school {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
}

.chat-button {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--border-radius-md);
  cursor: pointer;
  text-decoration: none;
  display: flex;
  align-items: center;
  gap: var(--spacing-xs);
  font-size: var(--font-size-sm);
  transition: all var(--transition-normal);
  white-space: nowrap;
}

.chat-button:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-sm);
}

.product-actions {
  display: flex;
  gap: var(--spacing-md);
  margin-top: var(--spacing-sm);
}

.action-button {
  flex: 1;
  padding: var(--spacing-md);
  font-size: var(--font-size-md);
  border-radius: var(--border-radius-md);
  cursor: pointer;
  transition: all var(--transition-normal);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-xs);
}

.action-button.chat-button {
  background: var(--primary-color);
  color: white;
  border: none;
}

.action-button.chat-button:hover {
  background: var(--primary-hover);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.action-button.favorite-button {
  border: 1px solid var(--border-primary);
  background: var(--bg-primary);
  color: var(--text-secondary);
}

.action-button.favorite-button:hover {
  border-color: var(--warning-color);
  color: var(--warning-color);
}

.action-button.share-button {
  border: 1px solid var(--border-primary);
  background: var(--bg-primary);
  color: var(--text-secondary);
}

.action-button.share-button:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

/* 商品详情 */
.product-detail-section {
  background: var(--bg-primary);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-md);
  overflow: hidden;
}

.section-tabs {
  display: flex;
  background: var(--bg-secondary);
  border-bottom: 1px solid var(--border-secondary);
}

.tab-button {
  flex: 1;
  padding: var(--spacing-md);
  background: transparent;
  border: none;
  font-size: var(--font-size-md);
  font-weight: 500;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all var(--transition-normal);
  position: relative;
}

.tab-button:hover {
  color: var(--primary-color);
  background: var(--bg-quaternary);
}

.tab-button.active {
  color: var(--primary-color);
  background: var(--bg-primary);
  border-bottom: 2px solid var(--primary-color);
}

.tab-content {
  padding: var(--spacing-xl);
}

.product-description-section {
  margin-bottom: var(--spacing-xl);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-size: var(--font-size-xl);
  font-weight: 600;
  margin: 0 0 var(--spacing-xl);
  color: var(--text-primary);
}

.section-icon {
  font-size: var(--font-size-lg);
  color: var(--primary-color);
}

.description-content {
  font-size: var(--font-size-md);
  line-height: 1.8;
  color: var(--text-secondary);
  white-space: pre-wrap;
  padding: var(--spacing-lg);
  background: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
}

.product-trade-info {
  margin-top: var(--spacing-xl);
}

.info-title {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin: 0 0 var(--spacing-lg);
  color: var(--text-primary);
}

.info-item {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md) 0;
  border-bottom: 1px solid var(--border-secondary);
}

.info-label {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
  min-width: 80px;
}

.info-value {
  font-size: var(--font-size-sm);
  color: var(--text-secondary);
}

.location-link {
  color: var(--primary-color);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.location-link:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

.product-seller-info {
  margin-top: var(--spacing-xl);
}

.seller-card {
  background: var(--bg-secondary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
}

.seller-card-link {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
  text-decoration: none;
  color: var(--text-primary);
  transition: all var(--transition-normal);
}

.seller-card-link:hover {
  color: var(--primary-color);
}

.seller-avatar-large {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: var(--font-size-2xl);
  font-weight: bold;
  flex-shrink: 0;
  box-shadow: var(--shadow-md);
}

.seller-details-large {
  flex: 1;
}

.seller-name-large {
  font-size: var(--font-size-lg);
  font-weight: 600;
  margin-bottom: var(--spacing-xs);
}

.seller-school-large {
  font-size: var(--font-size-sm);
  color: var(--text-tertiary);
}

.view-more-icon {
  font-size: var(--font-size-lg);
  color: var(--text-tertiary);
  transition: transform var(--transition-normal);
}

.seller-card-link:hover .view-more-icon {
  transform: translateX(5px);
  color: var(--primary-color);
}

.action-button.buy-button {
  background: var(--success-color);
  color: white;
  border: none;
}

.action-button.buy-button:hover {
  background: var(--success-color);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 相关推荐 */
.related-products-section {
  background: var(--bg-primary);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-md);
  padding: var(--spacing-xl);
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
  margin: 0;
  color: var(--text-primary);
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

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: var(--spacing-lg);
}

/* 加载状态 */
.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  background: var(--bg-primary);
  border-radius: var(--border-radius-xl);
  box-shadow: var(--shadow-md);
}

.loading-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-secondary);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.loading-text {
  font-size: var(--font-size-md);
  color: var(--text-secondary);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .product-basic-section {
    grid-template-columns: 1fr;
    gap: var(--spacing-lg);
  }
  
  .product-images-section {
    order: 1;
  }
  
  .product-info-section {
    order: 2;
  }
  
  .main-image {
    max-width: 100%;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
    gap: var(--spacing-md);
  }
}

@media (max-width: 768px) {
  .product-detail-container {
    gap: var(--spacing-lg);
    padding: var(--spacing-md) 0;
  }
  
  .product-basic-section {
    padding: var(--spacing-lg);
  }
  
  .product-title {
    font-size: var(--font-size-xl);
  }
  
  .price-value {
    font-size: var(--font-size-2xl);
  }
  
  .product-actions {
    flex-direction: column;
    gap: var(--spacing-sm);
  }
  
  .action-button {
    width: 100%;
  }
  
  .tab-content {
    padding: var(--spacing-lg);
  }
  
  .related-products-section {
    padding: var(--spacing-lg);
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: var(--spacing-sm);
  }
}

@media (max-width: 480px) {
  .product-basic-section {
    padding: var(--spacing-md);
  }
  
  .product-title {
    font-size: var(--font-size-lg);
  }
  
  .price-value {
    font-size: var(--font-size-xl);
  }
  
  .product-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
  
  .thumbnail-item {
    width: 60px;
    height: 60px;
  }
  
  .tab-content {
    padding: var(--spacing-md);
  }
  
  .related-products-section {
    padding: var(--spacing-md);
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--spacing-sm);
  }
}
</style>
