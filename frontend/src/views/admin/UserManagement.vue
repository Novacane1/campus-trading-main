<template>
  <div class="user-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-input
              v-model="searchQuery"
              placeholder="搜索用户名/邮箱/手机号"
              style="width: 300px"
              clearable
              @clear="handleSearch"
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
          </div>
          <div class="header-right">
            <el-button type="primary">新增用户</el-button>
            <el-button type="danger" :disabled="!selectedUsers.length">批量禁用</el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="users"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="用户信息" width="250">
          <template #default="scope">
            <div class="user-info-cell">
              <el-avatar :size="32">{{ scope.row.username.charAt(0) }}</el-avatar>
              <div class="user-detail">
                <div class="username">{{ scope.row.username }}</div>
                <div class="email">{{ scope.row.email }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="role" label="角色" width="120">
          <template #default="scope">
            <el-tag :type="scope.row.role === 'admin' ? 'danger' : 'info'">
              {{ scope.row.role === 'admin' ? '管理员' : '普通用户' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-switch
              v-model="scope.row.active"
              active-color="var(--success-color)"
              inactive-color="var(--danger-color)"
              @change="toggleUserStatus(scope.row)"
            />
          </template>
        </el-table-column>
        <el-table-column prop="regDate" label="注册时间" sortable width="180" />
        <el-table-column prop="reputation" label="信誉分" sortable width="120">
          <template #default="scope">
            <el-rate v-model="scope.row.reputation" disabled show-score text-color="var(--warning-color)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" fixed="right" width="280">
          <template #default="scope">
            <el-button size="small" @click="editUser(scope.row)">编辑</el-button>
            <el-button
              size="small"
              :type="scope.row.can_publish ? 'warning' : 'success'"
              @click="togglePublish(scope.row)"
            >{{ scope.row.can_publish ? '禁止发布' : '允许发布' }}</el-button>
            <el-button size="small" type="danger" @click="deleteUser(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          :total="total"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>

    <!-- 编辑用户对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑用户" width="480px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="学校">
          <el-input v-model="editForm.school_name" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="信誉分">
          <el-input-number v-model="editForm.credit_score" :min="0" :max="100" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="submitEditUser">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminAPI from '../../services/adminAPI'

const searchQuery = ref('')
const selectedUsers = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const users = ref([])

const fetchUsers = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getUsers({
      page: currentPage.value,
      limit: pageSize.value,
      search: searchQuery.value || undefined
    })
    const data = res.data
    users.value = (data.users || []).map(u => ({
      id: u.id,
      username: u.username || '',
      email: u.email || '',
      school_name: u.school_name || '',
      phone: u.phone || '',
      student_id: u.student_id || '',
      role: u.student_id === 'admin' ? 'admin' : 'user',
      active: (u.credit_score || 0) > 0,
      can_publish: u.can_publish !== false,
      regDate: u.created_at ? new Date(u.created_at).toLocaleString('zh-CN') : '',
      reputation: u.credit_score || 0
    }))
    total.value = data.total || 0
  } catch (e) {
    ElMessage.error('获取用户列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchUsers()
}

const handleSelectionChange = (val) => {
  selectedUsers.value = val
}

const toggleUserStatus = async (row) => {
  try {
    const newScore = row.active ? 60 : 0
    await adminAPI.updateUser(row.id, { credit_score: newScore })
    ElMessage.success(`用户 ${row.username} 已${row.active ? '启用' : '禁用'}`)
  } catch (e) {
    row.active = !row.active
    ElMessage.error('操作失败')
  }
}

const editDialogVisible = ref(false)
const editLoading = ref(false)
const editForm = ref({ id: null, username: '', school_name: '', email: '', credit_score: 60 })

const editUser = (row) => {
  editForm.value = {
    id: row.id,
    username: row.username,
    school_name: row.school_name || '',
    email: row.email || '',
    credit_score: row.reputation || 60
  }
  editDialogVisible.value = true
}

const submitEditUser = async () => {
  editLoading.value = true
  try {
    await adminAPI.updateUser(editForm.value.id, {
      credit_score: editForm.value.credit_score,
      school_name: editForm.value.school_name
    })
    ElMessage.success('用户信息已更新')
    editDialogVisible.value = false
    fetchUsers()
  } catch (e) {
    ElMessage.error('更新失败')
  } finally {
    editLoading.value = false
  }
}

const togglePublish = async (row) => {
  const newVal = !row.can_publish
  const action = newVal ? '允许' : '禁止'
  try {
    await adminAPI.togglePublish(row.id, newVal)
    row.can_publish = newVal
    ElMessage.success(`已${action}用户 ${row.username} 发布商品`)
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

const deleteUser = (row) => {
  ElMessageBox.confirm(`确定要删除用户 ${row.username} 吗？`, '警告', {
    type: 'warning'
  }).then(async () => {
    try {
      await adminAPI.deleteUser(row.id)
      ElMessage.success('删除成功')
      fetchUsers()
    } catch (e) {
      ElMessage.error('删除失败')
    }
  }).catch(() => {})
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchUsers()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchUsers()
}

onMounted(() => {
  fetchUsers()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.user-info-cell {
  display: flex;
  align-items: center;
  gap: 12px;
}

.user-detail {
  display: flex;
  flex-direction: column;
}

.username {
  font-weight: bold;
  color: var(--text-primary);
}

.email {
  font-size: 12px;
  color: var(--text-tertiary);
}

.pagination-container {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
