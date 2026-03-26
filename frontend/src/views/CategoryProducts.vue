<template>
  <div class="category-products-container">
    <!-- 分类信息 -->
    <div class="category-header">
      <h1 class="category-title">{{ categoryName }}</h1>
      <div class="category-breadcrumb">
        <router-link to="/">首页</router-link>
        <span class="separator">/</span>
        <router-link to="/categories">分类</router-link>
        <span class="separator">/</span>
        <span class="current-category">{{ categoryName }}</span>
      </div>
    </div>
    
    <!-- 筛选和排序 -->
    <div class="filter-section">
      <div class="filter-group">
        <span class="filter-label">价格区间：</span>
        <el-radio-group v-model="priceRange" size="small" @change="handleFilterChange">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="0-50">50元以下</el-radio-button>
          <el-radio-button value="50-200">50-200元</el-radio-button>
          <el-radio-button value="200-500">200-500元</el-radio-button>
          <el-radio-button value="500-">500元以上</el-radio-button>
        </el-radio-group>
      </div>
      <div class="filter-group">
        <span class="filter-label">商品状态：</span>
        <el-radio-group v-model="productStatus" size="small" @change="handleFilterChange">
          <el-radio-button value="all">全部</el-radio-button>
          <el-radio-button value="on_sale">在售</el-radio-button>
          <el-radio-button value="sold">已售</el-radio-button>
        </el-radio-group>
      </div>
      <div class="filter-group">
        <span class="filter-label">交易地点：</span>
        <el-select v-model="location" placeholder="全部地点" size="small" class="filter-select" @change="handleFilterChange">
          <el-option label="全部地点" value="" />
          <el-option
            v-for="loc in locations"
            :key="loc.id"
            :label="loc.name"
            :value="loc.name"
          />
        </el-select>
      </div>
      <div class="filter-group">
        <span class="filter-label">排序方式：</span>
        <el-radio-group v-model="sortBy" size="small" @change="handleSortChange">
          <el-radio-button value="latest">最新发布</el-radio-button>
          <el-radio-button value="popular">最热门</el-radio-button>
          <el-radio-button value="price_asc">价格低到高</el-radio-button>
          <el-radio-button value="price_desc">价格高到低</el-radio-button>
        </el-radio-group>
      </div>
    </div>
    
    <!-- 商品列表 -->
    <div class="products-section">
      <div class="products-grid" v-if="products.length > 0">
        <product-card 
          v-for="product in products" 
          :key="product.id" 
          :product="product"
        />
      </div>
      <div class="empty-state" v-else>
        <el-icon class="empty-icon"><i class="el-icon-s-goods"></i></el-icon>
        <p class="empty-text">该分类下暂无商品</p>
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
import { useRoute, useRouter } from 'vue-router'
import ProductCard from '../components/ProductCard.vue'
import productAPI from '../services/productAPI'
import locationAPI from '../services/locationAPI'

const route = useRoute()
const router = useRouter()

const categoryId = computed(() => route.params.id)
const categoryName = ref('加载中...')
const products = ref([])
const locations = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)

// 筛选条件
const priceRange = ref('all')
const productStatus = ref('all')
const location = ref('')
const sortBy = ref('latest')

// 加载分类商品
const loadCategoryProducts = async () => {
  loading.value = true
  try {
    // 构建筛选参数
    const params = {
      page: currentPage.value,
      limit: pageSize.value
    }
    
    // 添加筛选条件
    if (priceRange.value && priceRange.value !== 'all') {
      params.price_range = priceRange.value
    }
    if (productStatus.value && productStatus.value !== 'all') {
      params.status = productStatus.value
    }
    if (location.value) {
      params.location = location.value
    }
    if (sortBy.value) {
      params.sort = sortBy.value
    }
    
    // 获取商品列表
    const response = await productAPI.getCategoryProducts(categoryId.value, params)
    products.value = response.data.products || []
    total.value = response.data.total || 0
    categoryName.value = response.data.category_name || '分类商品'
  } catch (error) {
    console.error('获取分类商品失败:', error)
    products.value = []
    total.value = 0
    categoryName.value = '分类商品'
  } finally {
    loading.value = false
  }
}

// 加载交易地点
const loadLocations = async () => {
  try {
    const response = await locationAPI.getLocations()
    locations.value = response.data.locations || []
  } catch (error) {
    console.error('获取交易地点失败:', error)
    // 使用模拟数据
    locations.value = [
      { id: 1, name: '图书馆' },
      { id: 2, name: '食堂门口' },
      { id: 3, name: '教学楼' },
      { id: 4, name: '操场' },
      { id: 5, name: '宿舍楼' }
    ]
  }
}

// 处理筛选条件变化
const handleFilterChange = () => {
  currentPage.value = 1
  loadCategoryProducts()
}

// 处理排序方式变化
const handleSortChange = () => {
  currentPage.value = 1
  loadCategoryProducts()
}

// 处理页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadCategoryProducts()
}

// 处理每页条数变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadCategoryProducts()
}

// 监听分类ID变化
watch(categoryId, () => {
  currentPage.value = 1
  loadCategoryProducts()
})

onMounted(() => {
  loadLocations()
  loadCategoryProducts()
})
</script>

<style scoped>
.category-products-container {
  padding: 20px 0;
}

/* 分类头部 */
.category-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-secondary);
}

.category-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0 0 10px;
  color: var(--text-primary);
}

.category-breadcrumb {
  font-size: 14px;
  color: var(--text-tertiary);
}

.category-breadcrumb a {
  color: var(--primary-color);
  text-decoration: none;
}

.category-breadcrumb a:hover {
  text-decoration: underline;
}

.separator {
  margin: 0 8px;
}

.current-category {
  color: var(--text-primary);
  font-weight: bold;
}

/* 筛选区域 */
.filter-section {
  background: var(--bg-primary);
  padding: 24px;
  border-radius: 12px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 30px;
  border: 1px solid var(--border-secondary);
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-secondary);
}

.filter-group:last-child {
  padding-bottom: 0;
  border-bottom: none;
}

.filter-label {
  font-size: 14px;
  color: var(--text-secondary);
  white-space: nowrap;
  min-width: 70px;
  font-weight: 500;
}

.filter-select {
  min-width: 140px;
}

:deep(.el-radio-group) {
  flex-wrap: wrap;
  gap: 0;
}

:deep(.el-radio-button .el-radio-button__inner) {
  border-radius: 4px !important;
  border: 1px solid var(--border-primary) !important;
  margin-right: 8px;
  margin-bottom: 4px;
  box-shadow: none !important;
  background: var(--bg-secondary, var(--bg-secondary)) !important;
  color: var(--text-secondary) !important;
  font-size: 13px;
  padding: 6px 14px;
  transition: all 0.2s;
}

:deep(.el-radio-button .el-radio-button__inner:hover) {
  color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

:deep(.el-radio-button.is-active .el-radio-button__inner) {
  background: var(--primary-color) !important;
  color: var(--bg-primary) !important;
  border-color: var(--primary-color) !important;
}

:deep(.el-select__wrapper) {
  background-color: var(--bg-input, var(--bg-primary)) !important;
  box-shadow: 0 0 0 1px var(--border-primary) inset !important;
  border-radius: 4px !important;
}

:deep(.el-select__placeholder) {
  color: var(--text-tertiary) !important;
  -webkit-text-fill-color: var(--text-tertiary) !important;
}

:deep(.el-select__placeholder.is-transparent) {
  color: transparent !important;
  -webkit-text-fill-color: transparent !important;
}

:deep(.el-select__selected-item) {
  color: var(--text-primary) !important;
  -webkit-text-fill-color: var(--text-primary) !important;
}

/* 商品列表 */
.products-section {
  margin-bottom: 30px;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  background: var(--bg-primary);
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
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
  .category-title {
    font-size: 24px;
  }

  .filter-group {
    flex-wrap: wrap;
  }

  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
}

@media (max-width: 480px) {
  .category-header {
    margin-bottom: 20px;
  }
  
  .category-title {
    font-size: 20px;
  }
  
  .filter-section {
    padding: 15px;
    margin-bottom: 20px;
  }
  
  .products-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
}
</style>
