<template>
  <div class="publish-container">
    <h2 class="publish-title">发布商品</h2>
    <el-form
      ref="publishFormRef"
      :model="publishForm"
      :rules="publishRules"
      label-width="100px"
      class="publish-form"
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
          v-model="publishForm.title"
          placeholder="请输入商品标题（1-50字）"
          maxlength="50"
          show-word-limit
        />
      </el-form-item>
      
      <!-- 商品价格 -->
      <el-form-item label="商品价格" prop="price">
        <div style="display: flex; align-items: center; width: 100%">
          <el-input-number
            v-model="publishForm.price"
            :min="0.01"
            :step="0.01"
            :precision="2"
            placeholder="请输入商品价格"
            style="flex: 1"
          />
          <span style="margin-left: 8px; color: var(--text-secondary)">元</span>
        </div>
      </el-form-item>

      <!-- 商品数量 -->
      <el-form-item label="商品数量" prop="quantity">
        <div style="display: flex; align-items: center; width: 100%">
          <el-input-number
            v-model="publishForm.quantity"
            :min="1"
            :step="1"
            placeholder="请输入商品数量"
            style="flex: 1"
          />
          <span style="margin-left: 8px; color: var(--text-secondary)">件</span>
        </div>
        <div class="el-upload__tip" style="margin-top: 8px">
          设置商品库存数量，买家可以选择购买数量
        </div>
      </el-form-item>

      <!-- 商品成色 -->
      <el-form-item label="商品成色" prop="condition">
        <el-select
          v-model="publishForm.condition"
          placeholder="请选择商品成色"
          style="width: 100%"
        >
          <el-option label="全新" value="全新" />
          <el-option label="几乎全新" value="几乎全新" />
          <el-option label="稍有瑕疵" value="稍有瑕疵" />
          <el-option label="瑕疵较多" value="瑕疵较多" />
          <el-option label="7成新以下" value="7成新以下" />
        </el-select>
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
            children: 'children',
            checkStrictly: true,
            emitPath: true
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
          v-model="publishForm.location"
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
          v-model="publishForm.description"
          type="textarea"
          :rows="6"
          placeholder="请详细描述商品的成色、使用情况、瑕疵等信息（10-500字）"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>

      <!-- 可交易时间 -->
      <el-form-item label="可交易时间">
        <div class="time-location-section">
          <el-button type="primary" plain size="small" @click="showTimeDialog = true">
            选择时间段
          </el-button>
          <div v-if="publishForm.available_time_slots && publishForm.available_time_slots.length > 0" class="selected-items">
            <el-tag
              v-for="(slot, index) in publishForm.available_time_slots"
              :key="index"
              closable
              @close="removeTimeSlot(index)"
              style="margin: 4px"
            >
              {{ slot }}
            </el-tag>
          </div>
          <span v-else class="hint-text">选择您方便交易的时间段，有助于买家快速联系您</span>
        </div>
      </el-form-item>

      <!-- 偏好交易地点 -->
      <el-form-item label="偏好地点">
        <div class="time-location-section">
          <el-button type="primary" plain size="small" @click="showLocationDialog = true">
            选择地点
          </el-button>
          <div v-if="publishForm.preferred_locations && publishForm.preferred_locations.length > 0" class="selected-items">
            <el-tag
              v-for="(location, index) in publishForm.preferred_locations"
              :key="index"
              closable
              @close="removeLocation(index)"
              style="margin: 4px"
            >
              {{ location }}
            </el-tag>
          </div>
          <span v-else class="hint-text">选择您方便交易的地点，系统会自动匹配合适的买家</span>
        </div>
      </el-form-item>

      <!-- 商品状态 -->
      <el-form-item label="商品状态" prop="status">
        <el-radio-group v-model="publishForm.status">
          <el-radio value="available">在售</el-radio>
          <el-radio value="reserved">预留</el-radio>
        </el-radio-group>
      </el-form-item>
      
      <!-- 提交按钮 -->
      <el-form-item>
        <el-button type="primary" class="submit-button" @click="handleSubmit" :loading="loading">
          发布商品
        </el-button>
        <el-button class="cancel-button" @click="handleCancel">
          取消
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
        ref="categoryApplyForm"
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

    <!-- 选择时间段对话框 -->
    <el-dialog
      v-model="showTimeDialog"
      title="选择可交易时间"
      width="600px"
    >
      <div class="time-picker-row">
        <el-select v-model="timePickerDay" placeholder="周几" style="width: 120px">
          <el-option v-for="d in weekDays" :key="d" :label="d" :value="d" />
        </el-select>
        <el-select v-model="timePickerStart" placeholder="开始时间" style="width: 130px">
          <el-option v-for="t in hourOptions" :key="t" :label="t" :value="t" />
        </el-select>
        <span class="time-separator">至</span>
        <el-select v-model="timePickerEnd" placeholder="结束时间" style="width: 130px">
          <el-option v-for="t in hourOptions" :key="t" :label="t" :value="t" />
        </el-select>
        <el-button type="primary" @click="addTimeSlotFromPicker">添加</el-button>
      </div>
      <div v-if="selectedTimeSlots.length > 0" class="selected-time-tags">
        <el-tag
          v-for="(slot, index) in selectedTimeSlots"
          :key="index"
          closable
          @close="selectedTimeSlots.splice(index, 1)"
          style="margin: 4px"
        >
          {{ slot }}
        </el-tag>
      </div>
      <div v-else class="hint-text" style="margin-top: 12px">暂未添加时间段</div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTimeDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSaveTimeSlots">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 选择交易地点对话框 -->
    <el-dialog
      v-model="showLocationDialog"
      title="选择偏好交易地点"
      width="500px"
    >
      <el-checkbox-group v-model="selectedLocations" class="location-checkbox-group">
        <el-checkbox
          v-for="location in availableLocations"
          :key="location"
          :label="location"
          class="location-checkbox"
        >
          {{ location }}
        </el-checkbox>
      </el-checkbox-group>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showLocationDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSaveLocations">
            确定
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import productAPI from '../../services/productAPI'
import categoryAPI from '../../services/categoryAPI'
import locationAPI from '../../services/locationAPI'
import { getTimeSlots, getCommonLocations } from '../../services/timeLocationAPI'

const router = useRouter()
const publishFormRef = ref(null)
const categoryApplyFormRef = ref(null)
const loading = ref(false)
const categoryApplyLoading = ref(false)
const showCategoryApplyDialog = ref(false)
const showTimeDialog = ref(false)
const showLocationDialog = ref(false)

// 时间和地点选择
const availableTimeSlots = ref([])
const availableLocations = ref([])
const selectedTimeSlots = ref([])
const selectedLocations = ref([])

// 时间组合选择器
const weekDays = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
const hourOptions = [
  '08:00', '09:00', '10:00', '11:00', '12:00',
  '13:00', '14:00', '15:00', '16:00', '17:00',
  '18:00', '19:00', '20:00', '21:00', '22:00'
]
const timePickerDay = ref('')
const timePickerStart = ref('')
const timePickerEnd = ref('')

const addTimeSlotFromPicker = () => {
  if (!timePickerDay.value || !timePickerStart.value || !timePickerEnd.value) {
    ElMessage.warning('请选择完整的时间段（周几、开始时间、结束时间）')
    return
  }
  if (timePickerStart.value >= timePickerEnd.value) {
    ElMessage.warning('结束时间必须晚于开始时间')
    return
  }
  const slot = `${timePickerDay.value} ${timePickerStart.value}-${timePickerEnd.value}`
  if (selectedTimeSlots.value.includes(slot)) {
    ElMessage.warning('该时间段已添加')
    return
  }
  selectedTimeSlots.value.push(slot)
  timePickerDay.value = ''
  timePickerStart.value = ''
  timePickerEnd.value = ''
}

// 商品表单数据
const publishForm = reactive({
  title: '',
  price: '',
  quantity: 1,
  description: '',
  category_id: '',
  condition: '',
  location: '',
  status: 'available',
  images: [],
  available_time_slots: [],
  preferred_locations: []
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
const publishRules = {
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
  condition: [
    { required: true, message: '请选择商品成色', trigger: 'change' }
  ],
  location: [
    { required: true, message: '请选择交易地点', trigger: 'change' }
  ],
  images: [
    { type: 'array', required: true, min: 1, message: '请上传至少一张商品图片', trigger: 'change' }
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
  publishForm.images = fileList.map(f => f.raw || f)
}

// 处理图片删除
const handleImageRemove = (file, fileList) => {
  imageFiles.value = fileList
  publishForm.images = fileList.map(f => f.raw || f)
}

// 处理图片数量超出限制
const handleExceed = () => {
  ElMessage.warning('最多上传8张图片')
}

// 处理分类选择
const handleCategoryChange = (value) => {
  if (value && value.length > 0) {
    // 取最后一级分类ID
    publishForm.category_id = value[value.length - 1]
  } else {
    publishForm.category_id = ''
  }
}

// 处理时间段保存
const handleSaveTimeSlots = () => {
  publishForm.available_time_slots = [...selectedTimeSlots.value]
  showTimeDialog.value = false
  ElMessage.success('时间段设置成功')
}

// 处理地点保存
const handleSaveLocations = () => {
  publishForm.preferred_locations = [...selectedLocations.value]
  showLocationDialog.value = false
  ElMessage.success('地点设置成功')
}

// 移除单个时间段
const removeTimeSlot = (index) => {
  publishForm.available_time_slots.splice(index, 1)
}

// 移除单个地点
const removeLocation = (index) => {
  publishForm.preferred_locations.splice(index, 1)
}

// 处理表单提交
const handleSubmit = async () => {
  if (!publishFormRef.value) return

  publishFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        // 上传图片到服务器
        const imageUrls = []
        for (const file of imageFiles.value) {
          const raw = file.raw || file
          if (raw instanceof File) {
            const formData = new FormData()
            formData.append('image', raw)
            const uploadRes = await productAPI.uploadImage(formData)
            imageUrls.push(uploadRes.data.url)
          } else if (typeof file === 'string') {
            imageUrls.push(file)
          }
        }

        // 构建商品数据
        const productData = {
          title: publishForm.title,
          price: publishForm.price,
          quantity: publishForm.quantity || 1,
          description: publishForm.description,
          category_id: publishForm.category_id,
          condition: publishForm.condition,
          location: publishForm.location,
          status: publishForm.status,
          images: imageUrls,
          available_time_slots: publishForm.available_time_slots,
          preferred_locations: publishForm.preferred_locations
        }

        // 提交商品
        const response = await productAPI.createProduct(productData)
        ElMessage.success('商品发布成功')
        router.push(`/product/${response.data.id}`)
      } catch (error) {
        console.error('发布失败:', error)
        ElMessage.error(error?.response?.data?.msg || '发布失败，请重试')
      } finally {
        loading.value = false
      }
    }
  })
}

// 处理取消
const handleCancel = () => {
  router.push('/')
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
        ElMessage.success('分类申请提交成功，等待审核')
        
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

// 清理空 children 数组，避免 cascader 显示异常
const cleanCategories = (list) => {
  return list.map(cat => {
    const item = { id: cat.id, name: cat.name }
    if (cat.children && cat.children.length > 0) {
      item.children = cleanCategories(cat.children)
    }
    return item
  })
}

// 加载分类和地点数据
const loadData = async () => {
  // 加载分类
  try {
    const categoryResponse = await categoryAPI.getCategories()
    const data = categoryResponse.data
    const raw = Array.isArray(data) ? data : (data.categories || [])
    categories.value = cleanCategories(raw)
  } catch (error) {
    console.error('加载分类失败:', error)
    categories.value = []
  }

  // 加载交易地点
  try {
    const locationResponse = await locationAPI.getLocations()
    const data = locationResponse.data
    locations.value = Array.isArray(data) ? data : (data.locations || [])
  } catch (error) {
    console.error('加载地点失败:', error)
    locations.value = []
  }

  // 加载时间段选项
  try {
    const timeSlotsResponse = await getTimeSlots()
    availableTimeSlots.value = timeSlotsResponse.data || []
  } catch (error) {
    console.error('加载时间段失败:', error)
    availableTimeSlots.value = []
  }

  // 加载地点选项
  try {
    const locationsResponse = await getCommonLocations()
    availableLocations.value = locationsResponse.data || []
  } catch (error) {
    console.error('加载地点选项失败:', error)
    availableLocations.value = []
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.publish-container {
  background: var(--bg-primary);
  padding: 30px;
  border-radius: 8px;
  box-shadow: 0 2px 8px var(--black-alpha-10);
}

.publish-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: var(--text-primary);
}

.publish-form {
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

/* 时间地点选择区域 */
.time-location-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.hint-text {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 时间段选择对话框 */
.time-picker-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.time-separator {
  font-size: 14px;
  color: var(--text-secondary);
}

.selected-time-tags {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
}

/* 地点选择对话框 */
.location-checkbox-group {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
}

.location-checkbox {
  margin: 0;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  transition: all 0.3s;
  text-align: center;
}

.location-checkbox:hover {
  background-color: var(--bg-secondary);
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

/* 响应式设计 */
@media (max-width: 768px) {
  .publish-container {
    padding: 20px;
  }
  
  .publish-title {
    font-size: 20px;
    margin-bottom: 20px;
  }
  
  .publish-form {
    max-width: 100%;
  }
  
  .submit-button,
  .cancel-button {
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
  .publish-container {
    padding: 15px;
  }
  
  .publish-title {
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
