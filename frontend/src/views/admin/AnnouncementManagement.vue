<template>
  <div class="announcement-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-select v-model="filterStatus" placeholder="状态筛选" style="width: 130px" @change="handleSearch">
              <el-option label="全部状态" value="" />
              <el-option label="草稿" value="draft" />
              <el-option label="已发布" value="published" />
              <el-option label="已归档" value="archived" />
            </el-select>
          </div>
          <div class="header-right">
            <el-button type="primary" @click="openCreateDialog">发布公告</el-button>
          </div>
        </div>
      </template>

      <el-table :data="announcements" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="title" label="标题" min-width="200" show-overflow-tooltip />
        <el-table-column prop="priority" label="优先级" width="100">
          <template #default="scope">
            <el-tag :type="getPriorityType(scope.row.priority)">{{ getPriorityText(scope.row.priority) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="publisher_name" label="发布者" width="100" />
        <el-table-column prop="publish_time" label="发布时间" width="170" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button size="small" @click="viewAnnouncement(scope.row)">查看</el-button>
            <el-button size="small" type="primary" @click="editAnnouncement(scope.row)">编辑</el-button>
            <el-button v-if="scope.row.status === 'draft'" size="small" type="success" @click="publishAnnouncement(scope.row)">发布</el-button>
            <el-button size="small" type="danger" @click="deleteAnnouncement(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          :total="total"
          @size-change="fetchAnnouncements"
          @current-change="fetchAnnouncements"
        />
      </div>
    </el-card>

    <!-- 创建/编辑公告对话框 -->
    <el-dialog v-model="formDialogVisible" :title="isEdit ? '编辑公告' : '发布公告'" width="600px">
      <el-form :model="formData" label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="formData.title" placeholder="请输入公告标题" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="formData.content" type="textarea" :rows="6" placeholder="请输入公告内容" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="formData.priority" style="width: 100%">
            <el-option label="低" value="low" />
            <el-option label="普通" value="normal" />
            <el-option label="高" value="high" />
            <el-option label="紧急" value="urgent" />
          </el-select>
        </el-form-item>
        <el-form-item label="过期时间">
          <el-date-picker v-model="formData.expire_time" type="datetime" placeholder="选择过期时间" style="width: 100%" />
        </el-form-item>
        <el-form-item label="立即发布">
          <el-switch v-model="formData.publish_now" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="formDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">{{ isEdit ? '保存' : '创建' }}</el-button>
      </template>
    </el-dialog>

    <!-- 查看公告对话框 -->
    <el-dialog v-model="viewDialogVisible" title="公告详情" width="600px">
      <h3>{{ viewData.title }}</h3>
      <div class="announcement-meta">
        <el-tag :type="getPriorityType(viewData.priority)" size="small">{{ getPriorityText(viewData.priority) }}</el-tag>
        <span>发布者: {{ viewData.publisher_name }}</span>
        <span>发布时间: {{ viewData.publish_time || '-' }}</span>
      </div>
      <el-divider />
      <div class="announcement-content">{{ viewData.content }}</div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminAPI from '../../services/adminAPI'

const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const announcements = ref([])
const submitLoading = ref(false)

const formDialogVisible = ref(false)
const isEdit = ref(false)
const formData = ref({ id: null, title: '', content: '', priority: 'normal', expire_time: null, publish_now: false })

const viewDialogVisible = ref(false)
const viewData = ref({})

const fetchAnnouncements = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getAnnouncements({
      page: currentPage.value,
      limit: pageSize.value,
      status: filterStatus.value || undefined
    })
    announcements.value = res.data.announcements || []
    total.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('获取公告列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchAnnouncements()
}

const getPriorityType = (priority) => {
  const map = { low: 'info', normal: '', high: 'warning', urgent: 'danger' }
  return map[priority] || ''
}

const getPriorityText = (priority) => {
  const map = { low: '低', normal: '普通', high: '高', urgent: '紧急' }
  return map[priority] || priority
}

const getStatusType = (status) => {
  const map = { draft: 'info', published: 'success', archived: 'warning' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { draft: '草稿', published: '已发布', archived: '已归档' }
  return map[status] || status
}

const openCreateDialog = () => {
  isEdit.value = false
  formData.value = { id: null, title: '', content: '', priority: 'normal', expire_time: null, publish_now: false }
  formDialogVisible.value = true
}

const editAnnouncement = (row) => {
  isEdit.value = true
  formData.value = { ...row, publish_now: false }
  formDialogVisible.value = true
}

const viewAnnouncement = (row) => {
  viewData.value = row
  viewDialogVisible.value = true
}

const submitForm = async () => {
  if (!formData.value.title || !formData.value.content) {
    ElMessage.warning('请填写标题和内容')
    return
  }
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await adminAPI.updateAnnouncement(formData.value.id, formData.value)
      ElMessage.success('公告已更新')
    } else {
      await adminAPI.createAnnouncement(formData.value)
      ElMessage.success('公告已创建')
    }
    formDialogVisible.value = false
    fetchAnnouncements()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

const publishAnnouncement = async (row) => {
  try {
    await adminAPI.publishAnnouncement(row.id)
    ElMessage.success('公告已发布')
    fetchAnnouncements()
  } catch (e) {
    ElMessage.error('发布失败')
  }
}

const deleteAnnouncement = (row) => {
  ElMessageBox.confirm(`确定要删除公告 "${row.title}" 吗？`, '警告', { type: 'warning' })
    .then(async () => {
      try {
        await adminAPI.deleteAnnouncement(row.id)
        ElMessage.success('公告已删除')
        fetchAnnouncements()
      } catch (e) {
        ElMessage.error('删除失败')
      }
    }).catch(() => {})
}

onMounted(() => {
  fetchAnnouncements()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.pagination-container { margin-top: 24px; display: flex; justify-content: flex-end; }
.announcement-meta { display: flex; gap: 16px; align-items: center; color: #666; font-size: 14px; margin-top: 8px; }
.announcement-content { white-space: pre-wrap; line-height: 1.8; }
</style>
