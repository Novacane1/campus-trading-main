<template>
  <div class="profile-container" v-loading="loading">
    <h2 class="page-title">{{ isMyProfile ? '个人中心' : '用户主页' }}</h2>
    
    <div class="profile-content" v-if="displayedUserInfo.username || !loading">
      <!-- 个人信息 -->
      <div class="profile-section">
        <h3 class="section-title">个人信息</h3>
        <div class="profile-card">
          <div class="profile-avatar">
            {{ displayedUserInfo.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <div class="profile-details">
            <div class="detail-item">
              <span class="detail-label">用户名：</span>
              <span class="detail-value">{{ displayedUserInfo.username }}</span>
            </div>
            <div class="detail-item" v-if="isMyProfile">
              <span class="detail-label">手机号：</span>
              <span class="detail-value">{{ displayedUserInfo.phone }}</span>
            </div>
            <div class="detail-item" v-if="isMyProfile">
              <span class="detail-label">邮箱：</span>
              <span class="detail-value">{{ displayedUserInfo.email }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">学校：</span>
              <span class="detail-value">{{ displayedUserInfo.school || '未设置' }}</span>
            </div>
            <div class="detail-item" v-if="isMyProfile">
              <span class="detail-label">学号：</span>
              <span class="detail-value">{{ displayedUserInfo.studentId || '未设置' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">注册时间：</span>
              <span class="detail-value">{{ formatTime(displayedUserInfo.created_at) }}</span>
            </div>
          </div>
          <el-button v-if="isMyProfile" type="primary" class="edit-button" @click="showEditDialog = true">
            编辑资料
          </el-button>
        </div>
      </div>
      
      <!-- 时空偏好设置 -->
      <div class="profile-section" v-if="isMyProfile">
        <h3 class="section-title">交易偏好设置</h3>
        <div class="preference-card">
          <div class="preference-item">
            <div class="preference-header">
              <span class="preference-label">常用交易时间</span>
              <el-button type="primary" size="small" @click="showTimeDialog = true">
                设置时间
              </el-button>
            </div>
            <div class="preference-content">
              <el-space wrap v-if="displayedUserInfo.usual_time_slots && displayedUserInfo.usual_time_slots.length > 0">
                <el-tag
                  v-for="(slot, index) in displayedUserInfo.usual_time_slots"
                  :key="index"
                  type="success"
                  closable
                  @close="removeTimeSlot(index)"
                >
                  {{ slot }}
                </el-tag>
              </el-space>
              <span v-else class="empty-text">未设置常用交易时间</span>
            </div>
          </div>
          <div class="preference-item">
            <div class="preference-header">
              <span class="preference-label">常用交易地点</span>
              <el-button type="primary" size="small" @click="showLocationDialog = true">
                设置地点
              </el-button>
            </div>
            <div class="preference-content">
              <el-space wrap v-if="displayedUserInfo.usual_locations && displayedUserInfo.usual_locations.length > 0">
                <el-tag
                  v-for="(location, index) in displayedUserInfo.usual_locations"
                  :key="index"
                  type="success"
                  closable
                  @close="removeLocation(index)"
                >
                  {{ location }}
                </el-tag>
              </el-space>
              <span v-else class="empty-text">未设置常用交易地点</span>
            </div>
          </div>
          <div class="preference-tip">
            <el-icon><InfoFilled /></el-icon>
            <span>设置常用时间和地点后，系统会自动为您匹配合适的交易对象，提高交易效率</span>
          </div>
        </div>
      </div>

      <!-- 账号安全 -->
      <div class="profile-section" v-if="isMyProfile">
        <h3 class="section-title">账号安全</h3>
        <div class="security-card">
          <div class="security-item">
            <span class="security-label">密码</span>
            <span class="security-status" :class="{ 'secure': displayedUserInfo.password_secure }">
              {{ displayedUserInfo.password_secure ? '安全' : '需要修改' }}
            </span>
            <el-button type="primary" size="small" @click="showPasswordDialog = true">
              修改密码
            </el-button>
          </div>
          <div class="security-item">
            <span class="security-label">手机号验证</span>
            <span class="security-status" :class="{ 'secure': displayedUserInfo.phone_verified }">
              {{ displayedUserInfo.phone_verified ? '已验证' : '未验证' }}
            </span>
            <el-button type="primary" size="small" @click="verifyPhone">
              {{ displayedUserInfo.phone_verified ? '重新验证' : '验证' }}
            </el-button>
          </div>
          <div class="security-item">
            <span class="security-label">邮箱验证</span>
            <span class="security-status" :class="{ 'secure': displayedUserInfo.email_verified }">
              {{ displayedUserInfo.email_verified ? '已验证' : '未验证' }}
            </span>
            <el-button type="primary" size="small" @click="verifyEmail">
              {{ displayedUserInfo.email_verified ? '重新验证' : '验证' }}
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 用户统计 -->
      <div class="profile-section">
        <h3 class="section-title">{{ isMyProfile ? '我的统计' : '用户统计' }}</h3>
        <div class="stats-card">
          <div class="stat-item">
            <div class="stat-value">{{ userStats.products_count }}</div>
            <div class="stat-label">发布商品</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ userStats.sold_count }}</div>
            <div class="stat-label">已售商品</div>
          </div>
          <div class="stat-item" v-if="isMyProfile">
            <div class="stat-value">{{ userStats.bought_count }}</div>
            <div class="stat-label">已购商品</div>
          </div>
          <div class="stat-item" v-if="isMyProfile">
            <div class="stat-value">{{ userStats.favorites_count }}</div>
            <div class="stat-label">收藏商品</div>
          </div>
        </div>
      </div>

      <!-- 收到的评价 -->
      <div class="profile-section">
        <h3 class="section-title">{{ isMyProfile ? '我收到的评价' : '收到的评价' }}</h3>
        <div v-if="sellerReviews.reviews.length > 0" class="reviews-card">
          <div class="reviews-summary">
            <div class="reviews-avg">
              <span class="avg-score">{{ sellerReviews.avg_rating }}</span>
              <el-rate :model-value="sellerReviews.avg_rating" disabled size="large" />
              <span class="reviews-total">共 {{ sellerReviews.total_count }} 条评价</span>
            </div>
          </div>
          <div class="reviews-list">
            <div v-for="review in sellerReviews.reviews" :key="review.id" class="profile-review-item">
              <div class="profile-review-header">
                <div class="profile-review-avatar">
                  {{ review.reviewer?.username?.charAt(0).toUpperCase() || 'U' }}
                </div>
                <div class="profile-review-user">
                  <span class="profile-review-name">{{ review.reviewer?.username || '匿名用户' }}</span>
                  <span class="profile-review-time">{{ formatTime(review.created_at) }}</span>
                </div>
                <el-rate :model-value="review.rating" disabled size="small" v-if="review.rating" />
              </div>
              <div class="profile-review-content" v-if="review.content">
                {{ review.content }}
              </div>
              <div class="profile-review-content muted" v-else>用户未填写评价内容</div>
              <router-link
                v-if="review.item && review.item.id"
                :to="`/product/${review.item.id}`"
                class="profile-review-item-name item-link"
              >
                <el-icon><Goods /></el-icon>
                <span>{{ review.item.name }}</span>
              </router-link>
              <div v-else-if="review.item" class="profile-review-item-name">
                <el-icon><Goods /></el-icon>
                <span>{{ review.item.name }}</span>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="empty-reviews">
          <el-empty description="暂无评价" :image-size="80" />
        </div>
      </div>

      <!-- 发布的所有商品 -->
      <div class="profile-section">
        <h3 class="section-title">{{ isMyProfile ? '我发布的商品' : 'TA发布的商品' }}</h3>
        <div v-if="userProducts.length > 0" class="products-grid">
          <product-card 
            v-for="product in userProducts" 
            :key="product.id" 
            :product="product"
          />
        </div>
        <div v-else class="empty-products">
          <el-empty description="暂无发布商品" />
        </div>
      </div>
    </div>
    
    <!-- 编辑资料对话框 -->
    <el-dialog
      v-model="showEditDialog"
      title="编辑个人资料"
      width="500px"
    >
      <el-form
        ref="editFormRef"
        :model="editForm"
        :rules="editRules"
        label-width="80px"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="editForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="学校" prop="school">
          <el-input v-model="editForm.school" placeholder="请输入学校名称" />
        </el-form-item>
        <el-form-item label="学号" prop="studentId">
          <el-input v-model="editForm.studentId" placeholder="请输入学号" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showEditDialog = false">取消</el-button>
          <el-button type="primary" @click="handleEditProfile" :loading="loading">
            保存修改
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 修改密码对话框 -->
    <el-dialog
      v-model="showPasswordDialog"
      title="修改密码"
      width="500px"
    >
      <el-form
        ref="passwordFormRef"
        :model="passwordForm"
        :rules="passwordRules"
        label-width="80px"
      >
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" placeholder="请确认新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPasswordDialog = false">取消</el-button>
          <el-button type="primary" @click="handleChangePassword" :loading="loading">
            保存修改
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 设置常用时间对话框 -->
    <el-dialog
      v-model="showTimeDialog"
      title="设置常用交易时间"
      width="600px"
    >
      <div class="time-dialog-content">
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        >
          选择您通常方便交易的时间段，系统会自动为您匹配合适的买家/卖家
        </el-alert>
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
        <div v-else class="empty-text" style="margin-top: 12px">暂未添加时间段</div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showTimeDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSaveTimeSlots" :loading="loading">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 设置常用地点对话框 -->
    <el-dialog
      v-model="showLocationDialog"
      title="设置常用交易地点"
      width="600px"
    >
      <div class="location-dialog-content">
        <el-alert
          title="提示"
          type="info"
          :closable="false"
          show-icon
          style="margin-bottom: 20px"
        >
          选择您通常方便交易的地点，系统会自动为您匹配合适的买家/卖家
        </el-alert>
        <el-checkbox-group v-model="selectedLocations" class="locations-grid">
          <el-checkbox
            v-for="location in availableLocations"
            :key="location"
            :label="location"
            border
          >
            {{ location }}
          </el-checkbox>
        </el-checkbox-group>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showLocationDialog = false">取消</el-button>
          <el-button type="primary" @click="handleSaveLocations" :loading="loading">
            保存
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../../stores/user'
import { ElMessage } from 'element-plus'
import { InfoFilled, Goods } from '@element-plus/icons-vue'
import ProductCard from '../../components/ProductCard.vue'
import productAPI from '../../services/productAPI'
import authAPI from '../../services/authAPI'
import { getTimeSlots, getCommonLocations } from '../../services/timeLocationAPI'
import { getSellerReviews } from '../../services/reviewAPI'

const route = useRoute()
const userStore = useUserStore()
const showEditDialog = ref(false)
const showPasswordDialog = ref(false)
const showTimeDialog = ref(false)
const showLocationDialog = ref(false)
const loading = ref(false)
const isMyProfile = computed(() => {
  return !route.params.id || route.params.id === userStore.userInfo?.id?.toString()
})

const displayedUserInfo = ref({
  username: '',
  phone: '',
  email: '',
  school: '',
  studentId: '',
  created_at: '',
  password_secure: true,
  phone_verified: false,
  email_verified: false,
  usual_time_slots: [],
  usual_locations: []
})

const userStats = ref({
  products_count: 0,
  sold_count: 0,
  bought_count: 0,
  favorites_count: 0
})

const userProducts = ref([])
const sellerReviews = ref({ reviews: [], avg_rating: 0, total_count: 0 })

const fetchProfile = async () => {
  const userId = route.params.id || userStore.userInfo?.id
  if (!userId || userId === 'undefined') {
    displayedUserInfo.value = {}
    userProducts.value = []
    userStats.value = {
      products_count: 0,
      sold_count: 0,
      bought_count: 0,
      favorites_count: 0
    }
    loading.value = false
    return
  }
  
  if (isMyProfile.value) {
    if (userStore.isLoggedIn) {
      displayedUserInfo.value = { ...userStore.userInfo }
      userStats.value = {
        products_count: 0,
        sold_count: 0,
        bought_count: 0,
        favorites_count: 0
      }
      
      try {
        const response = await productAPI.getUserProducts(userStore.userInfo?.id, 'all')
        userProducts.value = response.data.products || []
        userStats.value.products_count = userProducts.value.length
      } catch (error) {
        console.error('获取个人商品失败:', error)
      }
    }
  } else {
    // Fetch other user's profile
    loading.value = true
    try {
      const [userResponse, productsResponse] = await Promise.all([
        authAPI.getUserById(userId),
        productAPI.getUserProducts(userId, 'all')
      ])
      const userData = userResponse.data || {}
      displayedUserInfo.value = {
        ...userData,
        school: userData.school || userData.school_name,
        studentId: userData.studentId || userData.student_id
      }
      userProducts.value = productsResponse.data.products || []
      userStats.value = {
        products_count: userProducts.value.length,
        sold_count: 0,
        bought_count: 0,
        favorites_count: 0
      }
    } catch (error) {
      console.error('获取用户信息失败:', error)
      const fallbackName = route.query.name
      const fallbackSchool = route.query.school
      if (fallbackName || fallbackSchool) {
        displayedUserInfo.value = {
          id: userId,
          username: fallbackName || `用户_${userId}`,
          school: fallbackSchool || '',
          created_at: ''
        }
        userProducts.value = []
        userStats.value = {
          products_count: 0,
          sold_count: 0,
          bought_count: 0,
          favorites_count: 0
        }
      } else if (error.response?.status === 404) {
        ElMessage.error('用户不存在')
      } else {
        ElMessage.error('获取用户信息失败')
      }
    } finally {
      loading.value = false
    }
  }
}

const fetchUserReviews = async () => {
  const userId = route.params.id || userStore.userInfo?.id
  if (!userId || userId === 'undefined') return
  try {
    const res = await getSellerReviews(userId)
    sellerReviews.value = res.data || { reviews: [], avg_rating: 0, total_count: 0 }
  } catch (error) {
    console.error('获取用户评价失败:', error)
  }
}

onMounted(() => {
  fetchProfile()
  fetchUserReviews()
})
watch(() => route.params.id, () => {
  fetchProfile()
  fetchUserReviews()
})

// 编辑资料表单
const editFormRef = ref(null)
const editForm = reactive({
  username: '',
  school: '',
  studentId: ''
})

watch(() => userStore.userInfo, (newVal) => {
  if (isMyProfile.value && newVal) {
    displayedUserInfo.value = { ...newVal }
    editForm.username = newVal.username
    editForm.school = newVal.school
    editForm.studentId = newVal.studentId
  }
}, { immediate: true })

const editRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 2, max: 20, message: '用户名长度2-20位', trigger: 'blur' }
  ],
  school: [
    { required: true, message: '请输入学校名称', trigger: 'blur' }
  ],
  studentId: [
    { required: true, message: '请输入学号', trigger: 'blur' }
  ]
}

// 修改密码表单
const passwordFormRef = ref(null)
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

const formatTime = (timeString) => {
  if (!timeString) return ''
  return new Date(timeString).toLocaleString('zh-CN')
}

const handleEditProfile = async () => {
  if (!editFormRef.value) return
  
  editFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.updateProfile(editForm)
        showEditDialog.value = false
        // 显示成功提示
      } catch (error) {
        console.error('更新失败:', error)
        // 显示错误提示
      } finally {
        loading.value = false
      }
    }
  })
}

const handleChangePassword = async () => {
  if (!passwordFormRef.value) return
  
  passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.changePassword(passwordForm)
        showPasswordDialog.value = false
        // 显示成功提示
      } catch (error) {
        console.error('修改密码失败:', error)
        // 显示错误提示
      } finally {
        loading.value = false
      }
    }
  })
}

const verifyPhone = () => {
  // 发送验证码到手机
  console.log('发送验证码到手机:', userInfo.value.phone)
  // 显示验证码输入对话框
}

const verifyEmail = () => {
  // 发送验证邮件
  console.log('发送验证邮件到:', userInfo.value.email)
  // 显示成功提示
}

// 时间地点设置
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

// 加载可用的时间段和地点
const loadTimeLocationOptions = async () => {
  try {
    const [timeSlotsRes, locationsRes] = await Promise.all([
      getTimeSlots(),
      getCommonLocations()
    ])
    availableTimeSlots.value = timeSlotsRes.data || []
    availableLocations.value = locationsRes.data || []
  } catch (error) {
    console.error('加载时间地点选项失败:', error)
  }
}

// 打开时间设置对话框时初始化选中项
watch(showTimeDialog, (newVal) => {
  if (newVal) {
    selectedTimeSlots.value = [...(displayedUserInfo.value.usual_time_slots || [])]
  }
})

// 打开地点设置对话框时初始化选中项
watch(showLocationDialog, (newVal) => {
  if (newVal) {
    selectedLocations.value = [...(displayedUserInfo.value.usual_locations || [])]
  }
})

// 保存时间段设置
const handleSaveTimeSlots = async () => {
  loading.value = true
  try {
    await userStore.updateProfile({
      usual_time_slots: selectedTimeSlots.value
    })
    displayedUserInfo.value.usual_time_slots = [...selectedTimeSlots.value]
    showTimeDialog.value = false
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存时间段失败:', error)
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

// 保存地点设置
const handleSaveLocations = async () => {
  loading.value = true
  try {
    await userStore.updateProfile({
      usual_locations: selectedLocations.value
    })
    displayedUserInfo.value.usual_locations = [...selectedLocations.value]
    showLocationDialog.value = false
    ElMessage.success('保存成功')
  } catch (error) {
    console.error('保存地点失败:', error)
    ElMessage.error('保存失败')
  } finally {
    loading.value = false
  }
}

// 移除时间段
const removeTimeSlot = async (index) => {
  const newTimeSlots = [...displayedUserInfo.value.usual_time_slots]
  newTimeSlots.splice(index, 1)
  try {
    await userStore.updateProfile({
      usual_time_slots: newTimeSlots
    })
    displayedUserInfo.value.usual_time_slots = newTimeSlots
    ElMessage.success('删除成功')
  } catch (error) {
    console.error('删除时间段失败:', error)
    ElMessage.error('删除失败')
  }
}

// 移除地点
const removeLocation = async (index) => {
  const newLocations = [...displayedUserInfo.value.usual_locations]
  newLocations.splice(index, 1)
  try {
    await userStore.updateProfile({
      usual_locations: newLocations
    })
    displayedUserInfo.value.usual_locations = newLocations
    ElMessage.success('删除成功')
  } catch (error) {
    console.error('删除地点失败:', error)
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  loadTimeLocationOptions()
})
</script>

<style scoped>
.profile-container {
  padding: 20px 0;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: var(--text-primary);
}

.profile-content {
  display: flex;
  flex-direction: column;
  gap: 30px;
}

/* 个人信息 */
.profile-section {
  background: var(--bg-primary);
  border-radius: 8px;
  box-shadow: var(--shadow-md);
  padding: 30px;
  border: 1px solid var(--border-secondary);
}

.section-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.profile-card {
  display: flex;
  align-items: center;
  gap: 30px;
}

.profile-avatar {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  font-weight: bold;
}

.profile-details {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 12px;
  color: var(--text-tertiary);
}

.detail-value {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.edit-button {
  padding: 8px 16px;
}

/* 账号安全 */
.security-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.security-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px 0;
  border-bottom: 1px solid var(--border-secondary);
}

.security-item:last-child {
  border-bottom: none;
}

.security-label {
  font-size: 14px;
  color: var(--text-primary);
}

.security-status {
  font-size: 14px;
  padding: 4px 8px;
  border-radius: 12px;
  background: var(--bg-quaternary);
  color: var(--text-secondary);
}

.security-status.secure {
  background: var(--success-alpha-10);
  color: var(--success-color);
}

/* 我的统计 */
.stats-card {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
  gap: 20px;
}

.stat-item {
  text-align: center;
  padding: 20px;
  background: var(--bg-secondary);
  border-radius: 8px;
  transition: all 0.3s;
  border: 1px solid var(--border-secondary);
}

.stat-item:hover {
  background: var(--bg-quaternary);
  transform: translateY(-2px);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--primary-color);
  margin-bottom: 5px;
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .profile-card {
    flex-direction: column;
    text-align: center;
    gap: 20px;
  }

  .profile-details {
    grid-template-columns: 1fr;
    gap: 10px;
  }

  .security-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
    text-align: left;
  }

  .stats-card {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 480px) {
  .profile-section {
    padding: 20px;
  }

  .profile-avatar {
    width: 80px;
    height: 80px;
    font-size: 32px;
  }

  .stats-card {
    grid-template-columns: repeat(2, 1fr);
    gap: 10px;
  }

  .stat-item {
    padding: 15px;
  }

  .stat-value {
    font-size: 20px;
  }
}

/* 交易偏好设置 */
.preference-card {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.preference-item {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.preference-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.preference-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.preference-content {
  padding: 12px;
  background: var(--bg-secondary);
  border-radius: 6px;
  min-height: 50px;
  display: flex;
  align-items: center;
}

.empty-text {
  color: var(--text-tertiary);
  font-size: 13px;
}

.preference-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: var(--info-alpha-10);
  border-radius: 6px;
  color: var(--info-color);
  font-size: 13px;
  line-height: 1.5;
}

/* 时间地点对话框 */
.time-dialog-content,
.location-dialog-content {
  max-height: 500px;
  overflow-y: auto;
}

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

.locations-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 12px;
}

.locations-grid .el-checkbox {
  margin: 0;
  width: 100%;
}

.time-slots-grid .el-checkbox.is-bordered,
.locations-grid .el-checkbox.is-bordered {
  padding: 10px 15px;
  border-radius: 6px;
  transition: all 0.3s;
}

.time-slots-grid .el-checkbox.is-bordered:hover,
.locations-grid .el-checkbox.is-bordered:hover {
  border-color: var(--primary-color);
  background: var(--primary-alpha-10);
}

.time-slots-grid .el-checkbox.is-checked.is-bordered,
.locations-grid .el-checkbox.is-checked.is-bordered {
  border-color: var(--primary-color);
  background: var(--primary-alpha-10);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 20px;
}

.empty-products {
  padding: 40px 0;
}

/* 评价区域样式 */
.reviews-card {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.reviews-summary {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 10px;
}

.reviews-avg {
  display: flex;
  align-items: center;
  gap: 12px;
}

.avg-score {
  font-size: 32px;
  font-weight: 700;
  color: var(--warning-color, #e6a23c);
}

.reviews-total {
  font-size: 13px;
  color: var(--text-tertiary);
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.profile-review-item {
  padding: 14px 16px;
  background: var(--bg-secondary);
  border-radius: 10px;
  transition: box-shadow 0.2s;
}

.profile-review-item:hover {
  box-shadow: var(--shadow-sm);
}

.profile-review-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.profile-review-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 13px;
  font-weight: 600;
  flex-shrink: 0;
}

.profile-review-user {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.profile-review-name {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.profile-review-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.profile-review-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 6px;
}

.profile-review-content.muted {
  color: var(--text-quaternary);
  font-style: italic;
}

.profile-review-item-name {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--text-tertiary);
}

.profile-review-item-name.item-link {
  text-decoration: none;
  color: var(--primary-color);
  cursor: pointer;
  transition: color 0.2s;
}

.profile-review-item-name.item-link:hover {
  color: var(--primary-hover);
  text-decoration: underline;
}

.empty-reviews {
  padding: 20px 0;
}
</style>
