<template>
  <div class="all-products-container">
    <div class="filter-section">
      <div class="filter-group">
        <span class="filter-label">价格区间：</span>
        <el-radio-group v-model="priceRange" size="small" @change="handleFilterChange">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="0-50">50元以下</el-radio-button>
          <el-radio-button label="50-200">50-200元</el-radio-button>
          <el-radio-button label="200-500">200-500元</el-radio-button>
          <el-radio-button label="500-">500元以上</el-radio-button>
        </el-radio-group>
      </div>

      <div class="filter-group">
        <span class="filter-label">商品状态：</span>
        <el-radio-group v-model="status" size="small" @change="handleFilterChange">
          <el-radio-button label="all">全部</el-radio-button>
          <el-radio-button label="on_sale">在售</el-radio-button>
          <el-radio-button label="sold">已售</el-radio-button>
        </el-radio-group>
      </div>

      <div class="filter-group">
        <span class="filter-label">交易地点：</span>
        <el-select v-model="location" placeholder="选择地点" size="small" @change="handleFilterChange" class="filter-select">
          <el-option label="全部地点" value="all" />
          <el-option v-for="loc in locations" :key="loc.id" :label="loc.name" :value="loc.name" />
        </el-select>
      </div>

      <div class="filter-group">
        <span class="filter-label">排序方式：</span>
        <el-radio-group v-model="sortBy" size="small" @change="handleSortChange">
          <el-radio-button label="latest">最新发布</el-radio-button>
          <el-radio-button label="popular">最热门</el-radio-button>
          <el-radio-button label="price_asc">价格低到高</el-radio-button>
          <el-radio-button label="price_desc">价格高到低</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <div v-loading="loading" class="products-grid-wrapper">
      <div v-if="products.length > 0" class="products-grid">
        <product-card 
          v-for="product in products" 
          :key="product.id" 
          :product="product"
        />
      </div>
      <el-empty v-else description="暂无商品" />
    </div>

    <div class="pagination-wrapper" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :total="total"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import ProductCard from '../../components/ProductCard.vue'
import productAPI from '../../services/productAPI'
import locationAPI from '../../services/locationAPI'

const products = ref([])
const locations = ref([])
const loading = ref(false)
const sortBy = ref('latest')
const priceRange = ref('all')
const status = ref('on_sale')
const location = ref('all')
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const fetchProducts = async () => {
  loading.value = true
  try {
    const params = {
      sort: sortBy.value,
      page: currentPage.value,
      limit: pageSize.value
    }
    if (priceRange.value && priceRange.value !== 'all') {
      params.price_range = priceRange.value
    }
    if (status.value && status.value !== 'all') {
      params.status = status.value
    }
    if (location.value && location.value !== 'all') {
      params.location = location.value
    }
    const response = await productAPI.getProducts(params)
    products.value = response.data.products || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('获取商品失败:', error)
    products.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

const loadLocations = async () => {
  try {
    const response = await locationAPI.getLocations()
    locations.value = response.data.locations || response.data || []
  } catch (error) {
    console.error('获取地点失败:', error)
    locations.value = [
      { id: 1, name: '图书馆' },
      { id: 2, name: '食堂门口' },
      { id: 3, name: '教学楼' },
      { id: 4, name: '操场' },
      { id: 5, name: '宿舍楼' }
    ]
  }
}

const handleSortChange = () => {
  currentPage.value = 1
  fetchProducts()
}

const handleFilterChange = () => {
  currentPage.value = 1
  fetchProducts()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchProducts()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  loadLocations()
  fetchProducts()
})
</script>

<style scoped>
.all-products-container {
  padding: 20px 0;
  color: var(--text-primary);
}

.filter-section {
  background: var(--bg-primary);
  padding: 20px;
  border-radius: var(--border-radius-lg);
  box-shadow: var(--shadow-sm);
  margin-bottom: 30px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  border: 1px solid var(--border-secondary);
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 15px;
}

.filter-label {
  font-weight: 600;
  min-width: 80px;
  color: var(--text-secondary);
}

.filter-select {
  width: 150px;
}

:deep(.el-input__wrapper) {
  background-color: var(--bg-input) !important;
  box-shadow: 0 0 0 1px var(--border-primary) inset !important;
}

:deep(.el-input__inner) {
  color: var(--text-primary) !important;
  -webkit-text-fill-color: var(--text-primary) !important;
}

:deep(.el-select__wrapper) {
  background-color: var(--bg-input, var(--bg-primary)) !important;
  box-shadow: 0 0 0 1px var(--border-primary) inset !important;
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

:deep(.el-select__caret) {
  color: var(--text-secondary) !important;
}

:deep(.el-select .el-input__wrapper) {
  background-color: var(--bg-input, var(--bg-primary)) !important;
}

:deep(.el-select .el-input__inner) {
  color: var(--text-primary) !important;
  -webkit-text-fill-color: var(--text-primary) !important;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 15px;
  flex-wrap: wrap;
}

:deep(.el-radio-group) {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  background: transparent !important;
}

:deep(.el-radio-button__inner) {
  background-color: var(--bg-primary) !important;
  color: var(--text-secondary) !important;
  border: 1px solid var(--border-primary) !important;
  border-radius: var(--border-radius-md) !important;
  box-shadow: none !important;
  padding: 8px 16px;
  transition: all 0.3s;
}

:deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-left: 1px solid var(--border-primary) !important;
  border-radius: var(--border-radius-md) !important;
}

:deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-radius: var(--border-radius-md) !important;
}
:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: var(--primary-color) !important;
  color: white !important;
  border-color: var(--primary-color) !important;
  box-shadow: -1px 0 0 0 var(--primary-color) !important;
}

:deep(.el-radio-button__inner:hover) {
  color: var(--primary-color) !important;
}

:deep(.el-select .el-input__wrapper) {
  background-color: var(--bg-input) !important;
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 25px;
}

.pagination-wrapper {
  margin-top: 50px;
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 15px;
  }
}

/* 视觉升级覆盖 */
.all-products-container {
  padding: 10px 0 6px;
}

.filter-section {
  border-radius: 20px;
  border: 1px solid var(--border-secondary);
  background:
    linear-gradient(165deg, var(--primary-alpha-08), var(--primary-alpha-02)),
    var(--bg-primary);
  box-shadow: var(--shadow-md);
  padding: 22px;
}

.filter-group {
  gap: 12px;
}

.filter-label {
  font-size: 14px;
  letter-spacing: 0.01em;
}

:deep(.el-radio-button__inner) {
  min-height: 34px;
  display: inline-flex;
  align-items: center;
}

:deep(.el-radio-button__inner:hover) {
  border-color: var(--primary-alpha-35) !important;
  background-color: var(--primary-alpha-08) !important;
}

:deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--gradient-primary) !important;
}

:deep(.el-select__wrapper) {
  min-height: 34px !important;
  border-radius: 10px !important;
}

.products-grid-wrapper {
  border-radius: 20px;
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
  padding: 16px;
}

.products-grid {
  gap: 20px;
}

.pagination-wrapper {
  margin-top: 36px;
}

@media (max-width: 1024px) {
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  }
}

@media (max-width: 768px) {
  .filter-section {
    padding: 16px;
    border-radius: 16px;
  }

  .filter-label {
    min-width: 72px;
  }

  .products-grid-wrapper {
    padding: 12px;
    border-radius: 16px;
  }

  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 12px;
  }
}
</style>
