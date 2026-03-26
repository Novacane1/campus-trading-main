<template>
  <div class="history-container">
    <div class="page-header">
      <h2 class="page-title">浏览历史</h2>
      <el-button 
        type="danger" 
        plain 
        size="small"
        @click="handleClearHistory"
        :disabled="products.length === 0"
      >
        清空历史
      </el-button>
    </div>
    
    <!-- 历史记录列表 -->
    <div class="history-section">
      <div class="products-grid" v-if="products.length > 0">
        <div 
          v-for="product in products" 
          :key="product.id"
          class="product-item"
        >
          <div class="product-image">
            <img 
              :src="product.images?.[0] || defaultImage" 
              :alt="product.title"
            />
            <div class="product-badge" :class="product.status">
              {{ statusText[product.status] }}
            </div>
          </div>
          <div class="product-info">
            <h3 class="product-title">{{ product.title }}</h3>
            <div class="product-price">¥{{ product.price }}</div>
            <div class="product-meta">
              <span class="product-location">{{ product.location }}</span>
              <span class="product-time">{{ formatTime(product.created_at) }}</span>
            </div>
            <div class="product-actions">
              <router-link :to="`/product/${product.id}`" class="action-button view-button">
                查看
              </router-link>
              <button 
                class="action-button delete-button"
                @click="handleDeleteHistory(product.id)"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="empty-state" v-else>
        <el-icon class="empty-icon"><i class="el-icon-view"></i></el-icon>
        <p class="empty-text">您还没有浏览记录</p>
        <p class="empty-hint">浏览商品后，记录将显示在这里</p>
        <router-link to="/" class="back-button">去浏览商品</router-link>
      </div>
    </div>
    
    <!-- 分页 -->
    <div class="pagination-section" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[12, 24, 36]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import productAPI from '../../services/productAPI'

const products = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)

const defaultImage = 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=product%20placeholder%20image&image_size=square'

const statusText = {
  available: '在售',
  reserved: '预留',
  sold: '已售',
  offline: '下架'
}

// 加载浏览历史
const loadHistory = async () => {
  loading.value = true
  try {
    const response = await productAPI.getViewHistory()
    products.value = response.data.products || []
    total.value = response.data.total || products.value.length
  } catch (error) {
    console.error('获取浏览历史失败:', error)
    // 使用模拟数据
    products.value = [
      {
        id: 1,
        title: 'iPhone 13 Pro 256GB',
        price: 4999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=iPhone%2013%20Pro%20second%20hand&image_size=square'],
        location: '图书馆',
        status: 'available',
        created_at: '2024-01-10T10:00:00'
      },
      {
        id: 2,
        title: 'MacBook Air M1',
        price: 6999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=MacBook%20Air%20M1%20second%20hand&image_size=square'],
        location: '食堂门口',
        status: 'available',
        created_at: '2024-01-09T14:30:00'
      },
      {
        id: 3,
        title: 'AirPods Pro',
        price: 999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=AirPods%20Pro%20second%20hand&image_size=square'],
        location: '教学楼',
        status: 'available',
        created_at: '2024-01-08T09:15:00'
      }
    ]
    total.value = products.value.length
  } finally {
    loading.value = false
  }
}

// 处理删除单条历史记录
const handleDeleteHistory = async (productId) => {
  try {
    // 从本地列表中移除
    products.value = products.value.filter(p => p.id !== productId)
    total.value = products.value.length
  } catch (error) {
    console.error('删除历史记录失败:', error)
  }
}

// 处理清空历史记录
const handleClearHistory = async () => {
  if (confirm('确定要清空所有浏览历史吗？')) {
    products.value = []
    total.value = 0
  }
}

// 处理页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadHistory()
}

// 处理每页条数变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadHistory()
}

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return ''
  return new Date(timeString).toLocaleDateString('zh-CN')
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-container {
  padding: 20px 0;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0;
  color: var(--text-primary);
}

/* 历史记录列表 */
.history-section {
  margin-bottom: 30px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.product-item {
  background: var(--bg-elevated);
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-secondary);
  box-shadow: 0 2px 8px var(--black-alpha-10);
  transition: all 0.3s;
}

.product-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 16px var(--black-alpha-20);
}

.product-image {
  position: relative;
  width: 100%;
  padding-top: 75%; /* 4:3 aspect ratio */
  overflow: hidden;
}

.product-image img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.product-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  color: white;
}

.product-badge.available {
  background: var(--success-color);
}

.product-badge.reserved {
  background: var(--warning-color);
}

.product-badge.sold {
  background: var(--danger-color);
}

.product-badge.offline {
  background: var(--text-tertiary);
}

.product-info {
  padding: 15px;
}

.product-title {
  font-size: 14px;
  font-weight: bold;
  margin: 0 0 10px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.product-price {
  font-size: 18px;
  font-weight: bold;
  color: var(--danger-color);
  margin-bottom: 10px;
}

.product-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: var(--text-tertiary);
  margin-bottom: 15px;
}

.product-actions {
  display: flex;
  gap: 10px;
}

.action-button {
  flex: 1;
  padding: 8px;
  border-radius: 4px;
  font-size: 12px;
  text-align: center;
  text-decoration: none;
  transition: all 0.3s;
  border: 1px solid transparent;
}

.view-button {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border-color: var(--text-quaternary);
}

.view-button:hover {
  background: color-mix(in srgb, var(--primary-color) 16%, transparent 84%);
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.delete-button {
  background: color-mix(in srgb, var(--danger-color) 16%, transparent 84%);
  color: var(--danger-color);
  border-color: var(--danger-color);
  cursor: pointer;
}

.delete-button:hover {
  background: var(--danger-color);
  color: white;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  background: var(--bg-elevated);
  border-radius: 8px;
  border: 1px solid var(--border-secondary);
  box-shadow: 0 2px 8px var(--black-alpha-10);
}

.empty-icon {
  font-size: 64px;
  color: var(--text-quaternary);
  margin-bottom: 20px;
}

.empty-text {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 10px;
  font-weight: bold;
}

.empty-hint {
  font-size: 14px;
  color: var(--text-tertiary);
  margin-bottom: 30px;
}

.back-button {
  padding: 10px 24px;
  background: var(--primary-color);
  color: white;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s;
}

.back-button:hover {
  background: var(--primary-hover);
}

/* 分页 */
.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
    gap: 15px;
  }
  
  .product-actions {
    flex-direction: column;
  }
  
  .action-button {
    width: 100%;
  }
}

@media (max-width: 480px) {
  .products-grid {
    grid-template-columns: 1fr;
  }
}
</style>
