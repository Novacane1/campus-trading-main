<template>
  <div class="search-container">
    <!-- 搜索信息 -->
    <div class="search-header">
      <h1 class="search-title">
        搜索结果: <span class="search-keyword">{{ keyword }}</span>
      </h1>
      <p class="search-stats" v-if="total > 0">
        找到 {{ total }} 件相关商品
      </p>
    </div>
    
    <!-- 筛选和排序 -->
    <div class="filter-section">
      <div class="filter-options">
        <div class="filter-group">
          <span class="filter-label">价格区间：</span>
          <el-select v-model="priceRange" placeholder="全部" @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="0-100元" value="0-100" />
            <el-option label="100-500元" value="100-500" />
            <el-option label="500-1000元" value="500-1000" />
            <el-option label="1000-5000元" value="1000-5000" />
            <el-option label="5000元以上" value="5000-" />
          </el-select>
        </div>
        <div class="filter-group">
          <span class="filter-label">商品状态：</span>
          <el-select v-model="productStatus" placeholder="全部" @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="在售" value="available" />
            <el-option label="预留" value="reserved" />
          </el-select>
        </div>
        <div class="filter-group">
          <span class="filter-label">交易地点：</span>
          <el-select v-model="location" placeholder="全部" @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option
              v-for="loc in locations"
              :key="loc.id"
              :label="loc.name"
              :value="loc.name"
            />
          </el-select>
        </div>
        <div class="filter-group">
          <span class="filter-label">商品成色：</span>
          <el-select v-model="condition" placeholder="全部" @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="全新" value="全新" />
            <el-option label="95新" value="95新" />
            <el-option label="9成新" value="9成新" />
            <el-option label="8成新及以下" value="8成新及以下" />
          </el-select>
        </div>
        <div class="filter-group">
          <span class="filter-label">发布时间：</span>
          <el-select v-model="timeRange" placeholder="全部" @change="handleFilterChange">
            <el-option label="全部" value="" />
            <el-option label="1天内" value="1" />
            <el-option label="3天内" value="3" />
            <el-option label="1周内" value="7" />
            <el-option label="1月内" value="30" />
          </el-select>
        </div>
      </div>
      <div class="sort-options">
        <span class="sort-label">排序方式：</span>
        <el-select v-model="sortBy" placeholder="默认" @change="handleSortChange">
          <el-option label="默认" value="" />
          <el-option label="价格从低到高" value="price_asc" />
          <el-option label="价格从高到低" value="price_desc" />
          <el-option label="最新发布" value="latest" />
          <el-option label="热门程度" value="popular" />
        </el-select>
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
        <el-icon class="empty-icon"><i class="el-icon-search"></i></el-icon>
        <p class="empty-text">未找到相关商品</p>
        <p class="empty-hint">请尝试其他关键词或筛选条件</p>
        <router-link to="/" class="back-button">返回首页</router-link>
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

const keyword = computed(() => route.query.keyword || '')
const products = ref([])
const locations = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(12)

// 筛选条件
const priceRange = ref('')
const productStatus = ref('')
const location = ref(route.query.location || '')
const condition = ref('')
const timeRange = ref('')
const sortBy = ref(route.query.sort || '')

// 加载搜索结果
const loadSearchResults = async () => {
  loading.value = true
  try {
    // 构建筛选参数
    const params = {
      keyword: keyword.value,
      page: currentPage.value,
      limit: pageSize.value
    }
    
    // 添加筛选条件
    if (priceRange.value) {
      params.price_range = priceRange.value
    }
    if (productStatus.value) {
      params.status = productStatus.value
    }
    if (location.value) {
      params.location = location.value
    }
    if (condition.value) {
      params.condition = condition.value
    }
    if (timeRange.value) {
      params.time_range = timeRange.value
    }
    if (sortBy.value) {
      params.sort = sortBy.value
    }
    
    // 获取商品列表
    const response = await productAPI.searchProducts(keyword.value, params)
    products.value = response.data.products || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('搜索失败:', error)
    // 使用模拟数据，根据关键字过滤
    let mockProducts = [
      {
        id: '1',
        title: 'iPhone 13 Pro',
        price: 4999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=iPhone%2013%20Pro%20second%20hand&image_size=square'],
        location: '图书馆',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 2).toISOString(),
        status: 'available',
        condition: '95新',
        seller_reputation: 4.8,
        views: 125,
        favorites: 32,
        chat_count: 15
      },
      {
        id: '2',
        title: 'MacBook Air M1',
        price: 6999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=MacBook%20Air%20M1%20second%20hand&image_size=square'],
        location: '食堂门口',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2).toISOString(),
        status: 'available',
        condition: '全新',
        seller_reputation: 5.0,
        views: 89,
        favorites: 25,
        chat_count: 10
      },
      {
        id: '3',
        title: 'AirPods Pro',
        price: 999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=AirPods%20Pro%20second%20hand&image_size=square'],
        location: '教学楼',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 5).toISOString(),
        status: 'available',
        condition: '9成新',
        seller_reputation: 4.5,
        views: 203,
        favorites: 45,
        chat_count: 28
      },
      {
        id: '4',
        title: 'iPad Pro 12.9',
        price: 5999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=iPad%20Pro%2012.9%20second%20hand&image_size=square'],
        location: '操场',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 10).toISOString(),
        status: 'available',
        condition: '95新',
        seller_reputation: 4.9,
        views: 67,
        favorites: 18,
        chat_count: 8
      },
      {
        id: '5',
        title: 'Apple Watch Series 7',
        price: 1999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Apple%20Watch%20Series%207%20second%20hand&image_size=square'],
        location: '宿舍楼',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 15).toISOString(),
        status: 'available',
        condition: '8成新及以下',
        seller_reputation: 4.2,
        views: 145,
        favorites: 30,
        chat_count: 12
      },
      {
        id: '6',
        title: 'iPhone 12',
        price: 3499,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=iPhone%2012%20second%20hand&image_size=square'],
        location: '图书馆',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 20).toISOString(),
        status: 'available',
        condition: '9成新',
        seller_reputation: 4.6,
        views: 189,
        favorites: 42,
        chat_count: 25
      },
      {
        id: '7',
        title: 'AirPods 2',
        price: 599,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=AirPods%202%20second%20hand&image_size=square'],
        location: '食堂门口',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 12).toISOString(),
        status: 'available',
        condition: '95新',
        seller_reputation: 4.7,
        views: 56,
        favorites: 12
      },
      {
        id: '8',
        title: 'MacBook Pro 14',
        price: 8999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=MacBook%20Pro%2014%20second%20hand&image_size=square'],
        location: '教学楼',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 18).toISOString(),
        status: 'available',
        condition: '全新',
        seller_reputation: 4.9,
        views: 34,
        favorites: 8
      },
      {
        id: '9',
        title: 'iPhone 14',
        price: 5999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=iPhone%2014%20second%20hand&image_size=square'],
        location: '操场',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 4).toISOString(),
        status: 'available',
        condition: '95新',
        seller_reputation: 4.8,
        views: 98,
        favorites: 23
      },
      {
        id: '10',
        title: 'iPad Air 5',
        price: 3999,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=iPad%20Air%205%20second%20hand&image_size=square'],
        location: '宿舍楼',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 6).toISOString(),
        status: 'available',
        condition: '9成新',
        seller_reputation: 4.4,
        views: 45,
        favorites: 15
      },
      {
        id: '11',
        title: 'Apple Watch SE',
        price: 1299,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=Apple%20Watch%20SE%20second%20hand&image_size=square'],
        location: '图书馆',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 8).toISOString(),
        status: 'available',
        condition: '95新',
        seller_reputation: 4.7,
        views: 67,
        favorites: 14
      },
      {
        id: '12',
        title: 'iPhone 13',
        price: 4499,
        images: ['https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=iPhone%2013%20second%20hand&image_size=square'],
        location: '食堂门口',
        created_at: new Date(Date.now() - 1000 * 60 * 60 * 24 * 12).toISOString(),
        status: 'available',
        condition: '9成新',
        seller_reputation: 4.6,
        views: 89,
        favorites: 21
      }
    ]
    
    // 根据关键字过滤商品
    if (keyword.value) {
      const searchKeyword = keyword.value.toLowerCase()
      mockProducts = mockProducts.filter(product => {
        return product.title.toLowerCase().includes(searchKeyword)
      })
    }
    
    // 应用筛选条件
    if (priceRange.value) {
      const [min, max] = priceRange.value.split('-').map(val => val ? parseInt(val) : null)
      mockProducts = mockProducts.filter(product => {
        if (min !== null && max !== null) {
          return product.price >= min && product.price <= max
        } else if (min !== null) {
          return product.price >= min
        } else if (max !== null) {
          return product.price <= max
        }
        return true
      })
    }
    
    if (productStatus.value) {
      mockProducts = mockProducts.filter(product => product.status === productStatus.value)
    }
    
    if (location.value) {
      mockProducts = mockProducts.filter(product => product.location === location.value)
    }

    if (condition.value) {
      mockProducts = mockProducts.filter(product => product.condition === condition.value)
    }

    if (timeRange.value) {
      const days = parseInt(timeRange.value)
      const now = new Date()
      mockProducts = mockProducts.filter(product => {
        const created = new Date(product.created_at)
        const diffDays = (now - created) / (1000 * 60 * 60 * 24)
        return diffDays <= days
      })
    }
    
    // 应用排序
    if (sortBy.value) {
      switch (sortBy.value) {
        case 'price_asc':
          mockProducts.sort((a, b) => a.price - b.price)
          break
        case 'price_desc':
          mockProducts.sort((a, b) => b.price - a.price)
          break
        case 'latest':
          mockProducts.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
          break
        case 'popular':
          mockProducts.sort((a, b) => (b.views + b.favorites) - (a.views + a.favorites))
          break
      }
    }
    
    total.value = mockProducts.length
    
    // 分页处理
    const startIndex = (currentPage.value - 1) * pageSize.value
    const endIndex = startIndex + pageSize.value
    products.value = mockProducts.slice(startIndex, endIndex)
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
  loadSearchResults()
}

// 处理排序方式变化
const handleSortChange = () => {
  currentPage.value = 1
  loadSearchResults()
}

// 处理页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadSearchResults()
}

// 处理每页条数变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadSearchResults()
}

// 监听关键词变化
watch(keyword, () => {
  currentPage.value = 1
  loadSearchResults()
})

// 监听location变化
watch(location, () => {
  currentPage.value = 1
  loadSearchResults()
})

onMounted(() => {
  loadLocations()
  loadSearchResults()
})
</script>

<style scoped>
.search-container {
  padding: 20px 0;
}

/* 搜索头部 */
.search-header {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--border-secondary);
}

.search-title {
  font-size: 24px;
  font-weight: bold;
  margin: 0 0 10px;
  color: var(--text-primary);
}

.search-keyword {
  color: var(--primary-color);
}

.search-stats {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
}

/* 筛选区域 */
.filter-section {
  background: var(--bg-primary);
  padding: 20px;
  border-radius: 8px;
  box-shadow: var(--shadow-sm);
  margin-bottom: 30px;
}

.filter-options {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 15px;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.filter-label {
  font-size: 14px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 15px;
  border-top: 1px solid var(--border-secondary);
}

.sort-label {
  font-size: 14px;
  color: var(--text-secondary);
}

:deep(.el-input__wrapper) {
  background-color: var(--bg-input, var(--bg-primary)) !important;
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
  .search-title {
    font-size: 20px;
  }
  
  .filter-options {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-group .el-select {
    flex: 1;
    min-width: 200px;
  }
  
  .products-grid {
    grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
    gap: 15px;
  }
}

@media (max-width: 480px) {
  .search-header {
    margin-bottom: 20px;
  }
  
  .search-title {
    font-size: 18px;
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
