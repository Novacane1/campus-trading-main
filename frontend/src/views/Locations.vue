<template>
  <div class="locations-container">
    <h2 class="page-title">交易地点管理</h2>
    
    <div class="locations-section">
      <div class="locations-grid">
        <div
          v-for="location in locations"
          :key="location.id"
          class="location-card"
        >
          <div class="location-image">
            <img :src="getLocationImage(location.name)" :alt="location.name" />
          </div>
          <div class="location-content">
            <h3 class="location-name">{{ location.name }}</h3>
            <p class="location-description">{{ location.description }}</p>
            <div class="location-meta">
              <span class="location-info">
                <span v-if="location.distance" class="location-distance">{{ location.distance }}</span>
                <span class="location-count">{{ location.usedCount || 0 }}次交易</span>
              </span>
              <span class="location-rating">{{ location.rating || 5.0 }}分</span>
            </div>
            <div class="location-actions">
              <router-link :to="`/search?location=${location.name}`" class="action-button view-button">
                查看商品
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div class="apply-location-section">
      <h2 class="section-title">申请新交易地点</h2>
      <div class="apply-location-card">
        <p class="apply-description">
          如果您发现校园内有适合的交易地点尚未添加，可以申请创建新的交易地点。我们会尽快审核您的申请。
        </p>
        <el-button type="primary" @click="showApplyDialog = true">
          申请新地点
        </el-button>
      </div>
    </div>
    
    <el-dialog
      v-model="showApplyDialog"
      title="申请新交易地点"
      width="500px"
    >
      <el-form
        ref="applyFormRef"
        :model="applyForm"
        :rules="applyRules"
        label-width="80px"
      >
        <el-form-item label="地点名称" prop="name">
          <el-input v-model="applyForm.name" placeholder="请输入地点名称" />
        </el-form-item>
        <el-form-item label="地点描述" prop="description">
          <el-input
            v-model="applyForm.description"
            type="textarea"
            :rows="3"
            placeholder="请输入地点描述"
          />
        </el-form-item>
        <el-form-item label="地点类型" prop="type">
          <el-select
            v-model="applyForm.type"
            placeholder="请选择地点类型"
          >
            <el-option label="教学楼" value="teaching_building" />
            <el-option label="图书馆" value="library" />
            <el-option label="食堂" value="canteen" />
            <el-option label="操场" value="playground" />
            <el-option label="宿舍楼" value="dormitory" />
            <el-option label="其他" value="other" />
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
import locationAPI from '../services/locationAPI'

const showApplyDialog = ref(false)
const applyFormRef = ref(null)
const loading = ref(false)
const locations = ref([])

const defaultLocationImages = {
  '图书馆': 'https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=400&h=250&fit=crop',
  '食堂门口': 'https://images.unsplash.com/photo-1567521464027-f127ff144326?w=400&h=250&fit=crop',
  '教学楼': 'https://images.unsplash.com/photo-1562774053-701939374585?w=400&h=250&fit=crop',
  '操场': 'https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=400&h=250&fit=crop',
  '宿舍楼': 'https://images.unsplash.com/photo-1555854877-bab0e564b8d5?w=400&h=250&fit=crop',
  '体育馆': 'https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=400&h=250&fit=crop'
}

const getLocationImage = (name) => {
  return defaultLocationImages[name] || 'https://images.unsplash.com/photo-1523050854058-8df90110c9f1?w=400&h=250&fit=crop'
}

const applyForm = ref({
  name: '',
  description: '',
  type: ''
})

const applyRules = {
  name: [
    { required: true, message: '请输入地点名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入地点描述', trigger: 'blur' }
  ],
  type: [
    { required: true, message: '请选择地点类型', trigger: 'change' }
  ]
}

const loadLocations = async () => {
  try {
    const response = await locationAPI.getLocations()
    locations.value = response.data.locations || []
  } catch (error) {
    console.error('获取交易地点失败:', error)
    locations.value = [
      {
        id: 1,
        name: '图书馆',
        description: '图书馆门口，环境安静，适合交易',
        status: 'active',
        product_count: 3
      },
      {
        id: 2,
        name: '食堂门口',
        description: '食堂门口，人流量大，交易方便',
        status: 'active',
        product_count: 3
      },
      {
        id: 3,
        name: '教学楼',
        description: '教学楼大厅，安全可靠',
        status: 'active',
        product_count: 2
      },
      {
        id: 4,
        name: '操场',
        description: '操场看台，适合大型物品交易',
        status: 'active',
        product_count: 2
      },
      {
        id: 5,
        name: '宿舍楼',
        description: '宿舍楼大厅，方便快捷',
        status: 'active',
        product_count: 2
      },
      {
        id: 6,
        name: '体育馆',
        description: '体育馆门口，适合运动器材交易',
        status: 'active',
        product_count: 0
      }
    ]
  }
}

const handleApply = async () => {
  if (!applyFormRef.value) return
  
  applyFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await locationAPI.applyLocation(applyForm.value)
        console.log('地点申请提交成功，等待审核')
        showApplyDialog.value = false
        applyForm.value = {
          name: '',
          description: '',
          type: ''
        }
      } catch (error) {
        console.error('地点申请失败:', error)
      } finally {
        loading.value = false
      }
    }
  })
}

const getStatusText = (status) => {
  const statusMap = {
    active: '启用',
    inactive: '停用',
    pending: '审核中'
  }
  return statusMap[status] || '未知'
}

onMounted(() => {
  loadLocations()
})
</script>

<style scoped>
.locations-container { padding: 20px 0; }
.page-title { font-size: 28px; font-weight: bold; margin-bottom: 30px; color: var(--text-primary); }
.locations-section { margin-bottom: 40px; }
.locations-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }

.location-card {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-secondary);
  transition: all 0.3s;
}
.location-card:hover { transform: translateY(-5px); box-shadow: var(--shadow-md); }

.location-image { width: 100%; height: 180px; overflow: hidden; }
.location-image img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s; }
.location-card:hover .location-image img { transform: scale(1.05); }

.location-content { padding: 20px; }
.location-name { font-size: 18px; font-weight: bold; margin: 0 0 8px; color: var(--text-primary); }
.location-description { font-size: 14px; color: var(--text-tertiary); line-height: 1.5; margin: 0 0 16px; }

.location-meta { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; font-size: 13px; }
.location-info { display: flex; gap: 12px; color: var(--text-tertiary); }
.location-distance { color: var(--primary-color); font-weight: 500; }
.location-count { color: var(--text-tertiary); }
.location-rating { color: var(--warning-color); font-weight: bold; }

.location-actions { margin-top: 4px; }
.action-button { display: inline-block; padding: 8px 20px; border-radius: var(--border-radius-md); font-size: 14px; text-decoration: none; transition: all 0.3s; }
.view-button { background: var(--primary-color); color: var(--bg-primary); }
.view-button:hover { background: var(--primary-hover); color: var(--bg-primary); }

.apply-location-section { margin-bottom: 40px; }
.section-title { font-size: 20px; font-weight: bold; margin-bottom: 20px; color: var(--text-primary); }
.apply-location-card {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: 30px;
  box-shadow: var(--shadow-sm);
  border: 1px solid var(--border-secondary);
  display: flex; flex-direction: column; align-items: center; text-align: center;
}
.apply-description { font-size: 14px; color: var(--text-tertiary); line-height: 1.6; margin-bottom: 30px; max-width: 600px; }

@media (max-width: 768px) {
  .page-title { font-size: 24px; margin-bottom: 20px; }
  .locations-grid { grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px; }
  .location-image { height: 140px; }
  .location-content { padding: 16px; }
  .apply-location-card { padding: 20px; }
}

@media (max-width: 480px) {
  .page-title { font-size: 20px; }
  .locations-grid { grid-template-columns: 1fr; gap: 10px; }
  .location-image { height: 120px; }
  .location-content { padding: 12px; }
  .location-name { font-size: 16px; }
  .location-description { font-size: 12px; }
}
</style>
