<template>
  <div class="product-card" :class="{ 'featured': product.isFeatured }">
    <router-link :to="`/product/${product.id}`" class="card-link">
      <div class="product-image">
        <img 
          :src="product.images?.[0] || defaultImage" 
          :alt="product.title"
          class="product-img"
          @error="handleImageError"
        />
        <div class="product-badge" v-if="product.status === 'sold'">已售</div>
        <div class="product-badge featured-badge" v-else-if="product.isFeatured">精选</div>
        <div class="image-overlay">
          <div class="overlay-actions">
            <button class="action-btn favorite-btn" @click.stop="handleFavorite" :class="{ 'favorited': isFavorited }">
              <el-icon><StarFilled v-if="isFavorited" /><Star v-else /></el-icon>
              <span>{{ isFavorited ? '已收藏' : '收藏' }}</span>
            </button>
            <button class="action-btn view-btn" @click.stop="handleQuickView">
              <el-icon><View /></el-icon>
              <span>详情</span>
            </button>
          </div>
        </div>
      </div>
      <div class="product-info">
        <div class="product-category" v-if="product.category">
          <router-link :to="`/category/${product.category.id}`" class="category-link">{{ product.category.name }}</router-link>
        </div>
        <h3 class="product-title">{{ product.title }}</h3>
        <div class="product-price">
          <span class="price-symbol">¥</span>
          <span class="price-value">{{ product.price }}</span>
        </div>
        <div class="product-meta">
          <div class="product-location">
            <el-icon class="location-icon"><Location /></el-icon>
            <span>{{ product.location }}</span>
          </div>
          <span class="product-time">{{ formatTime(product.created_at) }}</span>
        </div>
        <div class="product-stats">
          <span class="product-view">
            <el-icon class="stat-icon"><View /></el-icon>
            {{ product.views || 0 }}
          </span>
          <span class="product-favorite">
            <el-icon class="stat-icon"><Star /></el-icon>
            {{ product.favorites || 0 }}
          </span>
          <span class="product-chat" v-if="product.chat_count">
            <el-icon class="stat-icon"><ChatDotRound /></el-icon>
            {{ product.chat_count }}
          </span>
        </div>
      </div>
    </router-link>
    <div class="card-footer">
      <router-link
        v-if="sellerId"
        :to="{
          path: `/user/${sellerId}`,
          query: {
            name: sellerName || undefined,
            school: sellerSchool || undefined
          }
        }"
        class="seller-info"
      >
        <span class="seller-avatar">{{ sellerName?.charAt(0).toUpperCase() || 'U' }}</span>
        <div class="seller-detail">
          <span class="seller-name">{{ sellerName }}</span>
          <div class="seller-reputation" v-if="product.seller_reputation || product.seller?.credit_score">
            <el-icon class="star-icon"><StarFilled /></el-icon>
            <span>{{ product.seller_reputation || product.seller?.credit_score || 60 }}</span>
          </div>
        </div>
      </router-link>
      <div v-else class="seller-info">
        <span class="seller-avatar">U</span>
        <div class="seller-detail">
          <span class="seller-name">匿名用户</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { Star, StarFilled, View, Location, ChatDotRound } from '@element-plus/icons-vue'

const props = defineProps({
  product: {
    type: Object,
    required: true
  }
})

const sellerId = computed(() => {
  return props.product?.seller_id || props.product?.seller?.id || props.product?.user_id
})

const sellerName = computed(() => {
  return props.product?.seller?.username || props.product?.seller_name || '匿名用户'
})

const sellerSchool = computed(() => {
  return props.product?.seller?.school_name || props.product?.seller_school
})

const isFavorited = ref(false)
const defaultImage = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="400" viewBox="0 0 400 400"%3E%3Crect fill="%23f0f0f0" width="400" height="400"/%3E%3Ctext fill="%23999" font-family="Arial" font-size="16" x="50%25" y="50%25" text-anchor="middle" dy=".3em"%3E暂无图片%3C/text%3E%3C/svg%3E'

const handleImageError = (event) => {
  event.target.src = defaultImage
}

const formatTime = (timeString) => {
  if (!timeString) return ''
  
  const now = new Date()
  const time = new Date(timeString)
  const diff = now - time
  
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  
  return time.toLocaleDateString('zh-CN')
}

const handleFavorite = () => {
  isFavorited.value = !isFavorited.value
  ElMessage({
    message: isFavorited.value ? '已添加到收藏' : '已取消收藏',
    type: 'success',
    duration: 1500
  })
  // 这里可以添加实际的收藏API调用
}

const handleQuickView = () => {
  // 这里可以添加快速查看逻辑
  console.log('Quick view product:', props.product.id)
  ElMessage({
    message: '快速查看功能开发中',
    type: 'info',
    duration: 1500
  })
}
</script>

<style scoped>
.product-card {
  background-color: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-normal);
  display: flex;
  flex-direction: column;
  height: 100%;
  position: relative;
  border: 1px solid var(--border-secondary);
}

.product-card:hover {
  box-shadow: var(--shadow-lg);
}

.product-card.featured {
  border: 1px solid var(--primary-color);
}

.card-link {
  display: flex;
  flex-direction: column;
  height: 100%;
  text-decoration: none;
  color: var(--text-primary);
}

/* 商品图片 */
.product-image {
  position: relative;
  width: 100%;
  padding-top: 100%; /* 1:1 aspect ratio */
  overflow: hidden;
}

.product-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-card:hover .product-img {
  /* Remove scale */
}

/* 徽章 */
.product-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: linear-gradient(135deg, var(--danger-color), var(--danger-color));
  color: white;
  padding: 6px 12px;
  border-radius: var(--border-radius-md);
  font-size: var(--font-size-xs);
  font-weight: 500;
  z-index: 10;
  box-shadow: var(--shadow-sm);
}

.featured-badge {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  left: 12px;
  right: auto;
}

/* 图片悬停效果 */
.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to top, var(--black-alpha-60), transparent);
  opacity: 0;
  transition: opacity var(--transition-normal);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  padding: 16px;
}

.product-card:hover .image-overlay {
  opacity: 1;
}

.overlay-actions {
  display: flex;
  flex-direction: row;
  gap: 12px;
  transform: translateY(20px);
  transition: all var(--transition-normal);
  opacity: 0;
}

.product-image:hover .overlay-actions {
  transform: translateY(0);
  opacity: 1;
}

.action-btn {
  padding: 8px 16px;
  border-radius: var(--border-radius-md);
  background-color: var(--white-alpha-95);
  border: none;
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  transition: all var(--transition-normal);
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  box-shadow: var(--shadow-sm);
}

.action-btn:hover {
  background-color: var(--primary-color);
  color: white;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.favorite-btn.favorited {
  background-color: var(--warning-color);
  color: white;
}

.favorite-btn.favorited:hover {
  background-color: var(--warning-color);
}

/* 商品信息 */
.product-info {
  padding: 16px;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 分类 */
.product-category {
  display: inline-block;
  align-self: flex-start;
}

.category-link {
  font-size: var(--font-size-xs);
  color: var(--primary-color);
  text-decoration: none;
  background-color: var(--bg-quaternary);
  padding: 4px 10px;
  border-radius: var(--border-radius-md);
  transition: all var(--transition-fast);
}

.category-link:hover {
  background-color: var(--primary-color);
  color: white;
}

/* 标题 */
.product-title {
  font-size: var(--font-size-md);
  font-weight: 600;
  margin: 0;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  transition: color var(--transition-fast);
}

.card-link:hover .product-title {
  color: var(--primary-color);
}

/* 价格 */
.product-price {
  display: flex;
  align-items: baseline;
  gap: 2px;
  margin-top: 4px;
}

.price-symbol {
  font-size: var(--font-size-sm);
  color: var(--danger-color);
}

.price-value {
  font-size: var(--font-size-xl);
  font-weight: bold;
  color: var(--danger-color);
}

/* 元信息 */
.product-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: var(--font-size-xs);
  color: var(--text-tertiary);
}

.product-location {
  display: flex;
  align-items: center;
  gap: 4px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  flex: 1;
  margin-right: 10px;
}

.location-icon {
  font-size: 12px;
  flex-shrink: 0;
}

.product-time {
  white-space: nowrap;
  flex-shrink: 0;
}

/* 统计信息 */
.product-stats {
  display: flex;
  gap: 16px;
  font-size: var(--font-size-xs);
  color: var(--text-quaternary);
  margin-top: auto;
  padding-top: 10px;
  border-top: 1px solid var(--border-secondary);
}

.product-view,
.product-favorite,
.product-chat {
  display: flex;
  align-items: center;
  gap: 4px;
}

.stat-icon {
  font-size: 12px;
}

/* 卡片底部 */
.card-footer {
  padding: 12px 16px;
  border-top: 1px solid var(--border-secondary);
  background-color: var(--bg-quaternary);
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
  color: var(--text-secondary);
  font-size: var(--font-size-sm);
  transition: all var(--transition-fast);
}

.seller-info:hover {
  color: var(--primary-color);
}

.seller-avatar {
  display: inline-block;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color), var(--primary-hover));
  color: white;
  text-align: center;
  line-height: 32px;
  font-size: 14px;
  font-weight: bold;
  flex-shrink: 0;
}

.seller-detail {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}

.seller-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 120px;
  font-weight: 500;
}

.seller-reputation {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 11px;
  color: var(--warning-color);
}

.star-icon {
  font-size: 10px;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .product-info {
    padding: 14px;
    gap: 8px;
  }
  
  .product-title {
    font-size: var(--font-size-sm);
  }
  
  .price-value {
    font-size: var(--font-size-lg);
  }
  
  .card-footer {
    padding: 10px 14px;
  }
}

@media (max-width: 768px) {
  .product-info {
    padding: 12px;
  }
  
  .product-title {
    font-size: 13px;
  }
  
  .price-value {
    font-size: var(--font-size-md);
  }
  
  .product-meta,
  .product-stats {
    font-size: 11px;
  }
  
  .overlay-actions {
    gap: 8px;
  }
  
  .action-btn {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
  
  .card-footer {
    padding: 8px 12px;
  }
  
  .seller-name {
    max-width: 100px;
    font-size: 11px;
  }
}

/* 动画效果 */
@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.03);
  }
}

.product-card.featured {
  animation: pulse 2s infinite;
}

/* 加载动画 */
.product-img.loading {
  background: linear-gradient(90deg, var(--border-secondary) 25%, var(--border-primary) 50%, var(--border-secondary) 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% {
    background-position: 200% 0;
  }
  100% {
    background-position: -200% 0;
  }
}

/* 视觉升级覆盖 */
.product-card {
  border-radius: 18px;
  border: 1px solid var(--border-secondary);
  box-shadow: var(--shadow-sm);
}

.product-card:hover {
  transform: translateY(-4px);
  border-color: var(--primary-alpha-24);
  box-shadow: var(--shadow-md);
}

.product-card.featured {
  border-color: var(--primary-alpha-48);
  animation: none;
}

.product-image {
  padding-top: 88%;
}

.product-img {
  transition: transform var(--transition-slow), filter var(--transition-normal);
}

.product-card:hover .product-img {
  transform: scale(1.05);
  filter: saturate(1.04);
}

.image-overlay {
  background: linear-gradient(to top, var(--black-alpha-70), var(--black-alpha-10), transparent);
}

.overlay-actions {
  transform: translateY(10px);
}

.action-btn {
  border-radius: 999px;
  border: 1px solid var(--white-alpha-35);
  backdrop-filter: blur(6px);
  padding: 8px 14px;
}

.product-info {
  padding: 14px;
  gap: 8px;
}

.category-link {
  background: var(--primary-alpha-08);
  border: 1px solid transparent;
}

.category-link:hover {
  border-color: var(--primary-alpha-28);
}

.product-title {
  line-height: 1.45;
}

.price-value {
  font-size: 24px;
}

.product-meta {
  gap: 10px;
}

.product-stats {
  padding-top: 8px;
}

.card-footer {
  background:
    linear-gradient(170deg, var(--primary-alpha-08), var(--primary-alpha-02)),
    var(--bg-primary);
}

.seller-avatar {
  box-shadow: 0 10px 18px var(--primary-alpha-25);
}

@media (max-width: 768px) {
  .action-btn {
    width: auto;
    min-width: 36px;
    height: 36px;
    padding: 0 10px;
  }

  .action-btn span {
    display: none;
  }

  .product-image {
    padding-top: 96%;
  }

  .price-value {
    font-size: 20px;
  }
}

/* WP-DOS inspired overrides */
.product-card {
  border-radius: 6px;
  border: 1px solid var(--border-primary);
  box-shadow: none;
  background:
    linear-gradient(var(--bg-overlay), var(--bg-overlay)),
    url('../assets/dos_noise-texture.png');
  background-size: auto, 220px 220px;
}

.product-card:hover {
  border-color: var(--primary-color);
  transform: none;
  box-shadow: none;
}

.product-card.featured {
  border-color: var(--primary-color);
}

.product-badge {
  border-radius: 4px;
  box-shadow: none;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  background: color-mix(in srgb, var(--danger-color) 78%, var(--bg-primary) 22%);
}

.featured-badge {
  background: var(--gradient-primary);
  color: var(--bg-primary);
}

.image-overlay {
  background:
    repeating-linear-gradient(
      180deg,
      var(--primary-alpha-10) 0,
      var(--primary-alpha-10) 1px,
      transparent 1px,
      transparent 3px
    ),
    linear-gradient(to top, var(--black-alpha-80), var(--black-alpha-20), transparent);
}

.action-btn {
  border-radius: 4px;
  border: 1px solid var(--border-primary);
  background: var(--bg-input);
  color: var(--text-secondary);
  box-shadow: none;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.action-btn:hover {
  color: var(--bg-primary);
  border-color: var(--primary-color);
  background: var(--primary-color);
  transform: none;
  box-shadow: none;
}

.favorite-btn.favorited,
.favorite-btn.favorited:hover {
  background-color: var(--warning-color);
  border-color: var(--warning-color);
  color: var(--bg-primary);
}

.category-link {
  border-radius: 4px;
  border: 1px solid var(--border-primary);
  background: var(--bg-input);
  color: var(--text-secondary);
}

.category-link:hover {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: var(--bg-primary);
}

.product-title {
  text-transform: uppercase;
  letter-spacing: 0.06em;
  font-weight: 400;
}

.card-link:hover .product-title {
  color: var(--primary-color);
}

.price-symbol,
.price-value {
  color: var(--primary-color);
}

.price-value {
  font-size: 22px;
  font-weight: 500;
}

.product-meta {
  color: var(--text-tertiary);
}

.product-stats {
  border-top: 1px solid var(--border-secondary);
}

.card-footer {
  border-top: 1px solid var(--border-primary);
  background: color-mix(in srgb, var(--bg-elevated) 88%, black 12%);
}

.seller-info:hover {
  color: var(--text-primary);
}

.seller-avatar {
  border-radius: 4px;
  color: var(--bg-primary);
  box-shadow: none;
}
</style>
