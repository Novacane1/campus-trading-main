<template>
  <div class="audit-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-select v-model="filterType" placeholder="申请类型" style="width: 140px" @change="fetchApplications">
              <el-option label="全部类型" value="" />
              <el-option label="新分类" value="category" />
              <el-option label="新地点" value="location" />
            </el-select>
            <el-select v-model="filterStatus" placeholder="状态" style="width: 140px; margin-left: 12px" @change="fetchApplications">
              <el-option label="全部状态" value="" />
              <el-option label="待审核" value="pending" />
              <el-option label="已通过" value="approved" />
              <el-option label="已拒绝" value="rejected" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="applications" stripe style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="username" label="申请人" width="120" />
        <el-table-column label="类型" width="100">
          <template #default="scope">
            <el-tag :type="scope.row.app_type === 'category' ? '' : 'success'">
              {{ scope.row.app_type === 'category' ? '新分类' : '新地点' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="name" label="名称" min-width="150" />
        <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
        <el-table-column label="状态" width="100">
          <template #default="scope">
            <el-tag :type="statusType(scope.row.status)">{{ statusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="申请时间" width="180" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <template v-if="scope.row.status === 'pending'">
              <el-button size="small" type="success" @click="handleApprove(scope.row)">通过</el-button>
              <el-button size="small" type="danger" @click="handleReject(scope.row)">拒绝</el-button>
            </template>
            <span v-else-if="scope.row.status === 'rejected'" style="color: var(--text-tertiary)">
              {{ scope.row.reject_reason || '已拒绝' }}
            </span>
            <span v-else style="color: var(--success-color)">已通过</span>
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
          @size-change="fetchApplications"
          @current-change="fetchApplications"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminAPI from '../../services/adminAPI'

const filterType = ref('')
const filterStatus = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const applications = ref([])

const statusType = (s) => ({ pending: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info')
const statusText = (s) => ({ pending: '待审核', approved: '已通过', rejected: '已拒绝' }[s] || s)

const fetchApplications = async () => {
  try {
    const res = await adminAPI.getApplications({
      page: currentPage.value,
      limit: pageSize.value,
      type: filterType.value || undefined,
      status: filterStatus.value || undefined
    })
    applications.value = res.data.applications || []
    total.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('获取申请列表失败')
  }
}

const handleApprove = async (row) => {
  try {
    await adminAPI.approveApplication(row.id)
    ElMessage.success(`已通过「${row.name}」的申请`)
    row.status = 'approved'
  } catch (e) {
    ElMessage.error(e?.response?.data?.msg || '操作失败')
  }
}

const handleReject = (row) => {
  ElMessageBox.prompt('请输入拒绝原因（可选）', '拒绝申请', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputPlaceholder: '拒绝原因'
  }).then(async ({ value }) => {
    try {
      await adminAPI.rejectApplication(row.id, value || '')
      ElMessage.success('已拒绝该申请')
      row.status = 'rejected'
      row.reject_reason = value || ''
    } catch (e) {
      ElMessage.error(e?.response?.data?.msg || '操作失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchApplications()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
