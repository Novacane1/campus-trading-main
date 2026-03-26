<template>
  <div class="edit-container" v-if="product">
    <h2 class="edit-title">编辑商品</h2>
    <el-form
      ref="editFormRef"
      :model="editForm"
      :rules="editRules"
      label-width="100px"
      class="edit-form"
    >
      <!-- 商品图片上传 -->
      <el-form-item label="商品图片" prop="images">
        <el-upload
          class="image-uploader"
          action="#"
          :auto-upload="false"
          :on-change="handleImageChange"
          :on-remove="handleImageRemove"
          :file-list="imageFiles"
          list-type="picture-card"
          :limit="8"
          :on-exceed="handleExceed"
        >
          <el-icon><i class="el-icon-plus"></i></el-icon>
          <template #tip>
            <div class="el-upload__tip">
              最多上传8张图片，单张图片不超过5MB
            </div>
          </template>
        </el-upload>
      </el-form-item>
      
      <!-- 商品标题 -->
      <el-form-item label="商品标题" prop="title">
        <el-input
          v-model="editForm.title"
          placeholder="请输入商品标题（1-50字）"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>
      
      <!-- 商品价格 -->
      <el-form-item label="商品价格" prop="price">
        <el-input-number
          v-model="editForm.price"
          :min="0.01"
          :step="0.01"
          :precision="2"
          placeholder="请输入商品价格"
          style="width: 100%"
        />
      </el-form-item>
      
      <!-- 商品分类 -->
      <el-form-item label="商品分类" prop="category_id">
        <el-cascader
          v-model="selectedCategory"
          :options="categories"
          placeholder="请选择商品分类"
          :props="{
            value: 'id',
            label: 'name',
            children: 'children'
          }"
          @change="handleCategoryChange"
        />
        <div class="category-tip">
          <span v-if="!selectedCategory">如果没有找到合适的分类，可以</span>
          <el-button type="text" @click="showCategoryApplyDialog = true">申请新分类</el-button>
        </div>
      </el-form-item>
      
      <!-- 交易地点 -->
      <el-form-item label="交易地点" prop="location">
        <el-select
          v-model="editForm.location"
          placeholder="请选择交易地点"
          style="width: 100%"
        >
          <el-option
            v-for="location in locations"
            :key="location.id"
            :label="location.name"
            :value="location.name"
          />
        </el-select>
      </el-form-item>
      
      <!-- 商品描述 -->
      <el-form-item label="商品描述" prop="description">
        <el-input
          v-model="editForm.description"
          type="textarea"
          :rows="6"
          placeholder="请详细描述商品的成色、使用情况、瑕疵等信息（10-500字）"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      
      <!-- 商品状态 -->
      <el-form-item label="商品状态" prop="status">
        <el-radio-group v-model="editForm.status">
          <el-radio value="available">在售</el-radio>
          <el-radio value="reserved">预留</el-radio>
          <el-radio value="sold">已售</el-radio>
          <el-radio value="offline">下架</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <!-- 提交按钮 -->
      <el-form-item>
        <el-button type="primary" class="submit-button" @click="handleSubmit" :loading="loading">
          保存修改
        </el-button>
        <el-button class="cancel-button" @click="handleCancel">
          取消
        </el-button>
        <el-button type="danger" class="delete-button" @click="handleDelete" :loading="deleting">
          删除商品
        </el-button>
      </el-form-item>
    </el-form>
    
    <!-- 申请新分类对话框 -->
    <el-dialog
      v-model="showCategoryApplyDialog"
      title="申请新分类"
      width="500px"
    >
      <el-form
        ref="categoryApplyFormRef"
        :model="categoryApplyForm"
        :rules="categoryApplyRules"
        label-width="80px"
      >
        <el-form-item label="分类名称" prop="name">
          <el-input v-model="categoryApplyForm.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="分类描述" prop="description">
          <el-input
            v-model="categoryApplyForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入分类描述"
          />
        </el-form-item>
        <el-form-item label="上级分类" prop="parent_id">
          <el-select
            v-model="categoryApplyForm.parent_id"
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
          <el-button @click="showCategoryApplyDialog = false">取消</el-button>
          <el-button type="primary" @click="handleCategoryApply" :loading="categoryApplyLoading">
            提交申请
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
  <div class="loading-container" v-else>
    <el-skeleton :rows="10" animated />
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import productAPI from '../../services/productAPI'
import categoryAPI from '../../services/categoryAPI'
import locationAPI from '../../services/locationAPI'

const route = useRoute()
const router = useRouter()
const editFormRef = ref(null)
const categoryApplyFormRef = ref(null)
const loading = ref(false)
const deleting = ref(false)
const categoryApplyLoading = ref(false)
const showCategoryApplyDialog = ref(false)

const productId = computed(() => route.params.id)
const product = ref(null)

// 商品表单数据
const editForm = reactive({
  title: '',
  price: '',
  description: '',
  category_id: '',
  location: '',
  status: 'available',
  images: []
})

// 图片文件列表
const imageFiles = ref([])

// 选中的分类
const selectedCategory = ref([])

// 申请分类表单
const categoryApplyForm = reactive({
  name: '',
  description: '',
  parent_id: ''
})

// 分类和地点数据
const categories = ref([])
const locations = ref([])

// 表单验证规则
const editRules = {
  title: [
    { required: true, message: '请输入商品标题', trigger: 'blur' },
    { min: 1, max: 50, message: '标题长度1-50字', trigger: 'blur' }
  ],
  price: [
    { required: true, message: '请输入商品价格', trigger: 'blur' },
    { type: 'number', min: 0.01, message: '价格必须大于0', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入商品描述', trigger: 'blur' },
    { min: 10, max: 500, message: '描述长度10-500字', trigger: 'blur' }
  ],
  category_id: [
    { required: true, message: '请选择商品分类', trigger: 'change' }
  ],
  location: [
    { required: true, message: '请选择交易地点', trigger: 'change' }
  ],
  images: [
    { required: true, message: '请上传至少一张商品图片', trigger: 'change' }
  ]
}

const categoryApplyRules = {
  name: [
    { required: true, message: '请输入分类名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入分类描述', trigger: 'blur' }
  ]
}

// 处理图片上传
const handleImageChange = (file, fileList) => {
  imageFiles.value = fileList
}

// 处理图片删除
const handleImageRemove = (file, fileList) => {
  imageFiles.value = fileList
}

// 处理图片数量超出限制
const handleExceed = (files, fileList) => {
  console.error('最多上传8张图片')
}

// 处理分类选择
const handleCategoryChange = (value) => {
  if (value && value.length > 0) {
    // 取最后一级分类ID
    editForm.category_id = value[value.length - 1]
  } else {
    editForm.category_id = ''
  }
}

// 处理表单提交
const handleSubmit = async () => {
  if (!editFormRef.value) return
  
  editFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 处理图片上传
        // 这里简化处理，实际项目中需要上传图片到服务器
        const imageUrls = imageFiles.value.map(file => {
          // 模拟图片URL
          return 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=product%20image&image_size=square'
        })
        
        // 构建商品数据
        const productData = {
          ...editForm,
          images: imageUrls
        }
        
        // 更新商品
        await productAPI.updateProduct(productId.value, productData)
        
        // 保存成功，跳转到商品详情页
        router.push(`/product/${productId.value}`)
      } catch (error) {
        console.error('保存失败:', error)
        // 显示错误提示
      } finally {
        loading.value = false
      }
    }
  })
}

// 处理取消
const handleCancel = () => {
  router.push(`/product/${productId.value}`)
}

// 处理删除商品
const handleDelete = async () => {
  if (confirm('确定要删除这个商品吗？')) {
    deleting.value = true
    try {
      await productAPI.deleteProduct(productId.value)
      // 删除成功，跳转到我的商品页面
      router.push('/my-products')
    } catch (error) {
      console.error('删除失败:', error)
      // 显示错误提示
    } finally {
      deleting.value = false
    }
  }
}

// 处理分类申请
const handleCategoryApply = async () => {
  if (!categoryApplyFormRef.value) return
  
  categoryApplyFormRef.value.validate(async (valid) => {
    if (valid) {
      categoryApplyLoading.value = true
      try {
        // 提交分类申请
        await categoryAPI.applyCategory(categoryApplyForm)
        
        // 显示成功提示
        console.log('分类申请提交成功，等待审核')
        
        // 关闭对话框
        showCategoryApplyDialog.value = false
        
        // 重置表单
        categoryApplyForm.name = ''
        categoryApplyForm.description = ''
        categoryApplyForm.parent_id = ''
      } catch (error) {
        console.error('分类申请失败:', error)
        // 显示错误提示
      } finally {
        categoryApplyLoading.value = false
      }
    }
  })
}

// 加载商品详情
const loadProductDetail = async () => {
  loading.value = true
  try {
    const response = await productAPI.getProductById(productId.value)
    product.value = response.data
    
    // 填充表单数据
    editForm.title = product.value.title || product.value.name
    editForm.price = product.value.price
    editForm.description = product.value.description
    editForm.category_id = product.value.category_id
    editForm.location = product.value.location
    editForm.status = product.value.status
    editForm.images = product.value.images || []

    // 处理图片
    if (product.value.images && product.value.images.length > 0) {
      imageFiles.value = product.value.images.map(image => ({
        url: image
      }))
    }

    // 处理分类选择
    // 这里简化处理，实际项目中需要根据分类ID构建完整的分类路径
    if (editForm.category_id) {
      selectedCategory.value = [editForm.category_id]
    }
  } catch (error) {
    console.error('获取商品详情失败:', error)
    // 使用模拟数据
    product.value = {
      id: productId.value,
      title: 'iPhone 13 Pro 256GB',
      price: 4999,
      images: [
        'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=iPhone%2013%20Pro%20second%20hand&image_size=square'
      ],
      description: '出售iPhone 13 Pro 256GB，深空灰色，9成新，无划痕，电池健康度95%，配件齐全，包括充电器、数据线、包装盒等。因换新机出售，价格可小刀。',
      location: '图书馆',
      status: 'available',
      category_id: 11
    }
    
    // 填充表单数据
    editForm.title = product.value.title
    editForm.price = product.value.price
    editForm.description = product.value.description
    editForm.category_id = product.value.category_id
    editForm.location = product.value.location
    editForm.status = product.value.status
    editForm.images = product.value.images || []
    
    // 处理图片
    if (product.value.images && product.value.images.length > 0) {
      imageFiles.value = product.value.images.map(image => ({
        url: image
      }))
    }
    
    // 处理分类选择
    if (editForm.category_id) {
      selectedCategory.value = [editForm.category_id]
    }
  } finally {
    loading.value = false
  }
}

// 加载分类和地点数据
const loadData = async () => {
  try {
    // 加载分类
    const categoryResponse = await categoryAPI.getCategories()
    categories.value = categoryResponse.data.categories || categoryResponse.data || []
    
    // 加载交易地点
    const locationResponse = await locationAPI.getLocations()
    locations.value = locationResponse.data.locations || []
  } catch (error) {
    console.error('加载数据失败:', error)
    // 使用模拟数据
    categories.value = [
      { id: 1, name: '数码产品', children: [
        { id: 11, name: '手机' },
        { id: 12, name: '电脑' },
        { id: 13, name: '平板' },
        { id: 14, name: '耳机' }
      ]},
      { id: 2, name: '图书教材', children: [
        { id: 21, name: '专业课教材' },
        { id: 22, name: '公共课教材' },
        { id: 23, name: '考研资料' },
        { id: 24, name: '课外书' }
      ]},
      { id: 3, name: '运动装备', children: [
        { id: 31, name: '球类' },
        { id: 32, name: '健身器材' },
        { id: 33, name: '运动服装' },
        { id: 34, name: '其他' }
      ]},
      { id: 4, name: '生活用品', children: [
        { id: 41, name: '寝具' },
        { id: 42, name: '厨具' },
        { id: 43, name: '清洁用品' },
        { id: 44, name: '其他' }
      ]},
      { id: 5, name: '服装鞋包', children: [
        { id: 51, name: '上衣' },
        { id: 52, name: '裤子' },
        { id: 53, name: '鞋子' },
        { id: 54, name: '包包' }
      ]},
      { id: 6, name: '其他物品' }
    ]
    
    locations.value = [
      { id: 1, name: '图书馆' },
      { id: 2, name: '食堂门口' },
      { id: 3, name: '教学楼' },
      { id: 4, name: '操场' },
      { id: 5, name: '宿舍楼' }
    ]
  }
}

onMounted(() => {
  loadData()
  loadProductDetail()
})
</script>

<style scoped>
.edit-container {
  background: white;
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px var(--black-alpha-10);
}

.edit-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: var(--text-primary);
}

.edit-form {
  max-width: 800px;
}

/* 图片上传样式 */
.image-uploader {
  margin-bottom: 20px;
}

/* 分类提示 */
.category-tip {
  margin-top: 10px;
  font-size: 14px;
  color: var(--text-secondary);
}

/* 按钮样式 */
.submit-button {
  width: 200px;
  padding: 12px;
  font-size: 16px;
}

.cancel-button {
  margin-left: 20px;
  padding: 12px;
  font-size: 16px;
}

.delete-button {
  margin-left: 20px;
  padding: 12px;
  font-size: 16px;
}

/* 加载状态 */
.loading-container {
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px var(--black-alpha-10);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .edit-container {
    padding: 20px;
  }
  
  .edit-title {
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .edit-form {
    max-width: 100%;
  }
  
  .submit-button,
  .cancel-button,
  .delete-button {
    width: 100%;
    margin-left: 0;
    margin-top: 10px;
  }
  
  .el-form-item__label {
    width: 80px !important;
  }
  
  .el-form-item__content {
    margin-left: 90px !important;
  }
}

@media (max-width: 480px) {
  .edit-container {
    padding: 15px;
  }
  
  .edit-title {
    font-size: 18px;
  }
  
  .el-form-item__label {
    width: 70px !important;
    font-size: 12px;
  }
  
  .el-form-item__content {
    margin-left: 80px !important;
  }
}
</style>
