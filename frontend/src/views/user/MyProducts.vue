<template>
  <div class="my-products-container">
    <h2 class="page-title">我的商品</h2>
    
    <!-- 商品状态筛选 -->
    <div class="status-filter">
      <el-radio-group v-model="activeStatus" @change="handleStatusChange">
        <el-radio-button label="all">全部</el-radio-button>
        <el-radio-button label="available">在售</el-radio-button>
        <el-radio-button label="reserved">预留</el-radio-button>
        <el-radio-button label="sold">已售</el-radio-button>
        <el-radio-button label="offline">下架</el-radio-button>
      </el-radio-group>
    </div>
    
    <!-- 商品列表 -->
    <div class="products-section">
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
              <router-link :to="`/edit/${product.id}`" class="action-button edit-button">
                编辑
              </router-link>
              <button 
                class="action-button delete-button"
                @click="handleDelete(product.id)"
              >
                删除
              </button>
            </div>
          </div>
        </div>
      </div>
      <div class="empty-state" v-else>
        <el-icon class="empty-icon"><i class="el-icon-s-goods"></i></el-icon>
        <p class="empty-text">
          {{ activeStatus === 'all' ? '您还没有发布过商品' : `您没有${statusText[activeStatus]}的商品` }}
        </p>
        <router-link to="/publish" class="publish-button">发布商品</router-link>
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
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '../../stores/user'
import { ElMessage } from 'element-plus'
import productAPI from '../../services/productAPI'

const activeStatus = ref('all')
const products = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)
const deleting = ref(false)
const userStore = useUserStore()

const defaultImage = 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=product%20placeholder%20image&image_size=square'

const statusText = {
  all: '全部',
  available: '在售',
  reserved: '预留',
  sold: '已售',
  offline: '下架'
}

const statusMap = {
  available: 'on_sale',
  reserved: 'locked',
  sold: 'sold',
  offline: 'deleted'
}

// 加载商品列表
const loadProducts = async () => {
  loading.value = true
  try {
    const backendStatus = activeStatus.value === 'all' ? undefined : statusMap[activeStatus.value]
    const response = await productAPI.getUserProducts(userStore.userInfo?.id, backendStatus)
    products.value = response.data.products || []
    total.value = response.data.total || products.value.length
  } catch (error) {
    console.error('获取商品列表失败:', error)
    products.value = []
    total.value = 0
    ElMessage.error('获取商品列表失败')
  } finally {
    loading.value = false
  }
}

// 处理状态切换
const handleStatusChange = () => {
  currentPage.value = 1
  loadProducts()
}

// 处理页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadProducts()
}

// 处理每页条数变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadProducts()
}

// 处理删除商品
const handleDelete = async (productId) => {
  if (confirm('确定要删除这个商品吗？')) {
    deleting.value = true
    try {
      await productAPI.deleteProduct(productId)
      // 重新加载商品列表
      loadProducts()
    } catch (error) {
      console.error('删除商品失败:', error)
      if (error.response?.status === 404) {
        ElMessage.error('商品不存在或已删除')
      } else if (error.response?.status === 403) {
        ElMessage.error('无权限删除该商品')
      } else {
        ElMessage.error('删除商品失败')
      }
    } finally {
      deleting.value = false
    }
  }
}

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return ''
  return new Date(timeString).toLocaleDateString('zh-CN')
}

// 监听状态变化
watch(activeStatus, () => {
  currentPage.value = 1
  loadProducts()
})

onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.my-products-container {
  padding: 20px 0;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: var(--text-primary);
}

/* 状态筛选 */
.status-filter {
  margin-bottom: 30px;
}

/* 商品列表 */
.products-section {
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

.edit-button {
  background: color-mix(in srgb, var(--primary-color) 16%, transparent 84%);
  color: var(--primary-color);
  border-color: var(--primary-color);
}

.edit-button:hover {
  background: var(--primary-color);
  color: white;
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
  color: var(--text-tertiary);
  margin-bottom: 30px;
}

.publish-button {
  padding: 10px 24px;
  background: var(--primary-color);
  color: white;
  border-radius: 4px;
  text-decoration: none;
  font-size: 14px;
  transition: all 0.3s;
}

.publish-button:hover {
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
  
  .status-filter {
    margin-bottom: 20px;
  }
  
  .el-radio-group {
    display: flex;
    overflow-x: auto;
    padding-bottom: 10px;
  }
}
</style>
