<template>
  <div class="banner-management">
    <div class="page-header">
      <h2>Banner管理</h2>
      <el-button type="primary" @click="openCreateDialog">
        <el-icon><Plus /></el-icon>
        新增Banner
      </el-button>
    </div>

    <el-table :data="banners" v-loading="loading" style="width: 100%">
      <el-table-column label="排序" width="80" align="center">
        <template #default="{ row, $index }">
          <div class="sort-buttons">
            <el-button size="small" :disabled="$index === 0" @click="moveUp($index)" link>
              <el-icon><Top /></el-icon>
            </el-button>
            <el-button size="small" :disabled="$index === banners.length - 1" @click="moveDown($index)" link>
              <el-icon><Bottom /></el-icon>
            </el-button>
          </div>
        </template>
      </el-table-column>
      <el-table-column label="预览" width="200">
        <template #default="{ row }">
          <div class="banner-preview" :style="{ background: row.bg_color || '#f5f5f5' }">
            <span v-if="row.emoji" class="preview-emoji">{{ row.emoji }}</span>
            <img v-else-if="row.image" :src="row.image" class="preview-image" />
            <span v-else class="preview-placeholder">无图片</span>
          </div>
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="150" />
      <el-table-column prop="tag" label="标签" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.tag" size="small">{{ row.tag }}</el-tag>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
      <el-table-column prop="link" label="链接" width="120" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.link">{{ row.link }}</span>
          <span v-else class="text-muted">-</span>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.status === 'published' ? 'success' : 'info'" size="small">
            {{ row.status === 'published' ? '已发布' : '草稿' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" align="center">
        <template #default="{ row }">
          <el-button size="small" @click="openEditDialog(row)">编辑</el-button>
          <el-button
            size="small"
            :type="row.status === 'published' ? 'warning' : 'success'"
            @click="toggleStatus(row)"
          >
            {{ row.status === 'published' ? '下架' : '发布' }}
          </el-button>
          <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑Banner' : '新增Banner'"
      width="600px"
      @close="resetForm"
    >
      <el-form :model="form" :rules="rules" ref="formRef" label-width="80px">
        <el-form-item label="标题" prop="title">
          <el-input v-model="form.title" placeholder="请输入标题" />
        </el-form-item>
        <el-form-item label="标签" prop="tag">
          <el-input v-model="form.tag" placeholder="如：新品、热卖" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="请输入描述" />
        </el-form-item>
        <el-form-item label="展示方式">
          <el-radio-group v-model="displayMode">
            <el-radio value="emoji">Emoji</el-radio>
            <el-radio value="image">图片</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="displayMode === 'emoji'" label="Emoji">
          <el-input v-model="form.emoji" placeholder="输入一个emoji，如：🎉" style="width: 120px" />
        </el-form-item>
        <el-form-item v-else label="图片URL">
          <el-input v-model="form.image" placeholder="请输入图片URL" />
        </el-form-item>
        <el-form-item label="背景色">
          <el-color-picker v-model="bgColorPicker" show-alpha />
          <el-input v-model="form.bg_color" placeholder="或输入渐变色，如：linear-gradient(...)" style="margin-left: 12px; flex: 1" />
        </el-form-item>
        <el-form-item label="跳转链接">
          <el-input v-model="form.link" placeholder="点击后跳转的路径，如：/products" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitting">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Top, Bottom } from '@element-plus/icons-vue'
import adminAPI from '../../services/adminAPI'

const loading = ref(false)
const banners = ref([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const submitting = ref(false)
const formRef = ref(null)
const displayMode = ref('emoji')
const bgColorPicker = ref('')

const form = ref({
  id: null,
  title: '',
  tag: '',
  description: '',
  image: '',
  bg_color: '',
  emoji: '',
  link: ''
})

const rules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }]
}

watch(bgColorPicker, (val) => {
  if (val && !form.value.bg_color.includes('gradient')) {
    form.value.bg_color = val
  }
})

const fetchBanners = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getBanners()
    banners.value = res.data.banners || []
  } catch (e) {
    console.error('获取Banner列表失败:', e)
  } finally {
    loading.value = false
  }
}

const openCreateDialog = () => {
  isEdit.value = false
  form.value = { id: null, title: '', tag: '', description: '', image: '', bg_color: '', emoji: '', link: '' }
  displayMode.value = 'emoji'
  bgColorPicker.value = ''
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  form.value = { ...row }
  displayMode.value = row.emoji ? 'emoji' : 'image'
  bgColorPicker.value = row.bg_color?.startsWith('#') ? row.bg_color : ''
  dialogVisible.value = true
}

const resetForm = () => {
  formRef.value?.resetFields()
}

const submitForm = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const data = { ...form.value }
    if (displayMode.value === 'emoji') {
      data.image = ''
    } else {
      data.emoji = ''
    }

    if (isEdit.value) {
      await adminAPI.updateBanner(form.value.id, data)
      ElMessage.success('更新成功')
    } else {
      await adminAPI.createBanner(data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchBanners()
  } catch (e) {
    ElMessage.error(e.response?.data?.message || '操作失败')
  } finally {
    submitting.value = false
  }
}

const toggleStatus = async (row) => {
  const newStatus = row.status === 'published' ? 'draft' : 'published'
  try {
    await adminAPI.updateBanner(row.id, { status: newStatus })
    ElMessage.success(newStatus === 'published' ? '已发布' : '已下架')
    fetchBanners()
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除这个Banner吗？', '提示', { type: 'warning' })
    await adminAPI.deleteBanner(row.id)
    ElMessage.success('删除成功')
    fetchBanners()
  } catch (e) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

const moveUp = async (index) => {
  if (index === 0) return
  const ids = banners.value.map(b => b.id)
  ;[ids[index], ids[index - 1]] = [ids[index - 1], ids[index]]
  await updateSort(ids)
}

const moveDown = async (index) => {
  if (index === banners.value.length - 1) return
  const ids = banners.value.map(b => b.id)
  ;[ids[index], ids[index + 1]] = [ids[index + 1], ids[index]]
  await updateSort(ids)
}

const updateSort = async (ids) => {
  try {
    await adminAPI.sortBanners(ids)
    fetchBanners()
  } catch (e) {
    ElMessage.error('排序失败')
  }
}

onMounted(() => {
  fetchBanners()
})
</script>

<style scoped>
.banner-management {
  background: var(--bg-primary);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-lg);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--spacing-lg);
}

.page-header h2 {
  margin: 0;
  font-size: 20px;
}

.sort-buttons {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.banner-preview {
  width: 160px;
  height: 60px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.preview-emoji {
  font-size: 32px;
}

.preview-image {
  max-width: 100%;
  max-height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  color: #999;
  font-size: 12px;
}

.text-muted {
  color: var(--text-tertiary);
}
</style>
