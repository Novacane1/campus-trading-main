<template>
  <div class="categories-container">
    <h1 class="page-title">商品分类</h1>
    
    <!-- 分类列表 -->
    <div class="categories-section">
      <div class="categories-grid">
        <div 
          v-for="category in categories" 
          :key="category.id"
          class="category-card"
        >
          <router-link :to="`/category/${category.id}`" class="category-link">
            <div class="category-icon">
              <i :class="category.icon || 'el-icon-goods'" />
            </div>
            <h3 class="category-name">{{ category.name }}</h3>
            <p class="category-count">{{ category.productCount || 0 }}件商品</p>
          </router-link>
          
          <!-- 子分类 -->
          <div class="subcategories" v-if="category.children && category.children.length > 0">
            <router-link 
              v-for="subcategory in category.children" 
              :key="subcategory.id"
              :to="`/category/${subcategory.id}`"
              class="subcategory-item"
            >
              {{ subcategory.name }}
            </router-link>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 申请新分类 -->
    <div class="apply-category-section">
      <h2 class="section-title">申请新分类</h2>
      <div class="apply-category-card">
        <p class="apply-description">
          如果您找不到适合的商品分类，可以申请创建新的分类。我们会尽快审核您的申请。
        </p>
        <el-button type="primary" @click="showApplyDialog = true">
          申请新分类
        </el-button>
      </div>
    </div>
    
    <!-- 申请新分类对话框 -->
    <el-dialog
      v-model="showApplyDialog"
      title="申请新分类"
      width="500px"
    >
      <el-form
        ref="applyFormRef"
        :model="applyForm"
        :rules="applyRules"
        label-width="80px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="applyForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类描述" prop="description">
          <el-input
            v-model="applyForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          />
        </el-form-item>
        <el-form-item label="上级分类" prop="parent_id">
          <el-select
            v-model="applyForm.parent_id"
            placeholder="请选择上级分类（可选）"
          >
            <el-option label="无" value="" />
            <el-option
              v-for="category in categories"
              :key="category.id"
              :label="category.name"
              :value="category.id"
            />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showApplyDialog = false">取消</el-button>
          <el-button type="primary" @click="handleApply" :loading="loading">
            提交申请
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import categoryAPI from '../services/categoryAPI'

const showApplyDialog = ref(false)
const applyFormRef = ref(null)
const loading = ref(false)
const categories = ref([])

// 申请表单数据
const applyForm = ref({
  name: '',
  description: '',
  parent_id: ''
})

// 表单验证规则
const applyRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入分类描述', trigger: 'blur' }
  ]
}

// 加载分类数据
const loadCategories = async () => {
  try {
    const response = await categoryAPI.getCategories()
    categories.value = response.data || []
  } catch (error) {
    console.error('获取分类失败:', error)
    // 使用模拟数据
    categories.value = [
      { id: 1, name: '数码产品', icon: 'el-icon-electronics', productCount: 0 },
      { id: 2, name: '图书教材', icon: 'el-icon-document', productCount: 0 },
      { id: 3, name: '运动装备', icon: 'el-icon-position', productCount: 0 },
      { id: 4, name: '生活用品', icon: 'el-icon-home', productCount: 0 },
      { id: 5, name: '服装鞋包', icon: 'el-icon-suitcase', productCount: 0 },
      { id: 6, name: '其他物品', icon: 'el-icon-more-outline', productCount: 0 }
    ]
  }
}

// 处理分类申请
const handleApply = async () => {
  if (!applyFormRef.value) return
  
  applyFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await categoryAPI.applyCategory(applyForm.value)
        // 显示成功提示
        console.log('分类申请提交成功，等待审核')
        // 关闭对话框
        showApplyDialog.value = false
        // 重置表单
        applyForm.value = {
          name: '',
          description: '',
          parent_id: ''
        }
      } catch (error) {
        console.error('分类申请失败:', error)
        // 显示错误提示
      } finally {
        loading.value = false
      }
    }
  })
}

onMounted(() => {
  loadCategories()
})
</script>

<style scoped>
.categories-container {
  padding: 20px 0;
}

.page-title {
  font-size: 28px;
  font-weight: bold;
  margin-bottom: 30px;
  color: var(--text-primary);
}

/* 分类列表 */
.categories-section {
  margin-bottom: 40px;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.category-card {
  background: var(--bg-primary);
  border-radius: 8px;
  padding: 30px;
  box-shadow: var(--shadow-md);
  transition: all 0.3s;
  border: 1px solid var(--border-secondary);
}

.category-card:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
}

.category-link {
  text-decoration: none;
  color: var(--text-primary);
  display: flex;
  flex-direction: column;
  align-items: center;
}

.category-icon {
  width: 80px;
  height: 80px;
  background: var(--bg-quaternary);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 32px;
  color: var(--primary-color);
  margin-bottom: 20px;
  transition: all 0.3s;
}

.category-card:hover .category-icon {
  background: var(--primary-color);
  color: white;
  transform: scale(1.1);
}

.category-name {
  font-size: 18px;
  font-weight: bold;
  margin: 0 0 10px;
  text-align: center;
  color: var(--text-primary);
}

.category-count {
  font-size: 14px;
  color: var(--text-tertiary);
  margin: 0;
}

/* 子分类 */
.subcategories {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid var(--border-secondary);
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.subcategory-item {
  padding: 6px 12px;
  background: var(--bg-quaternary);
  border-radius: 16px;
  font-size: 12px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.3s;
}

.subcategory-item:hover {
  background: var(--primary-color);
  color: white;
}

/* 申请分类区域 */
.apply-category-section {
  margin-bottom: 40px;
}

.section-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.apply-category-card {
  background: var(--bg-primary);
  border-radius: 8px;
  padding: 30px;
  box-shadow: var(--shadow-md);
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  border: 1px solid var(--border-secondary);
}

.apply-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 30px;
  max-width: 600px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 24px;
    margin-bottom: 20px;
  }
  
  .categories-grid {
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 15px;
  }
  
  .category-card {
    padding: 20px;
  }
  
  .category-icon {
    width: 60px;
    height: 60px;
    font-size: 24px;
    margin-bottom: 15px;
  }
  
  .category-name {
    font-size: 16px;
  }
  
  .apply-category-card {
    padding: 20px;
  }
  
  .apply-description {
    margin-bottom: 20px;
  }
}

@media (max-width: 480px) {
  .page-title {
    font-size: 20px;
  }
  
  .categories-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }
  
  .category-card {
    padding: 15px;
  }
  
  .category-icon {
    width: 50px;
    height: 50px;
    font-size: 20px;
    margin-bottom: 10px;
  }
  
  .category-name {
    font-size: 14px;
  }
  
  .category-count {
    font-size: 12px;
  }
  
  .subcategories {
    margin-top: 15px;
    padding-top: 15px;
  }
  
  .subcategory-item {
    padding: 4px 8px;
    font-size: 11px;
  }
}
</style>
