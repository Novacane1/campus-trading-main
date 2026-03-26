<template>
  <div class="category-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>分类管理</span>
          <el-button type="primary" @click="openAddDialog">新增分类</el-button>
        </div>
      </template>

      <el-table :data="categories" stripe row-key="id" default-expand-all>
        <el-table-column prop="name" label="分类名称" min-width="200" />
        <el-table-column prop="icon" label="图标" width="100" />
        <el-table-column prop="sort_order" label="排序" width="100" sortable />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button size="small" type="primary" @click="openEditDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(scope.row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑分类' : '新增分类'" width="450px">
      <el-form :model="form" label-width="80px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="请输入分类名称" />
        </el-form-item>
        <el-form-item label="父分类">
          <el-select v-model="form.parent_id" placeholder="无（顶级分类）" clearable>
            <el-option v-for="c in parentOptions" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="图标">
          <el-input v-model="form.icon" placeholder="图标名称（可选）" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminAPI from '../../services/adminAPI'
import categoryAPI from '../../services/categoryAPI'

const categories = ref([])
const dialogVisible = ref(false)
const submitLoading = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const form = ref({ name: '', parent_id: null, icon: '', sort_order: 0 })

const parentOptions = computed(() => {
  return categories.value.filter(c => c.id !== editingId.value)
})

const fetchCategories = async () => {
  try {
    const res = await categoryAPI.getCategories()
    categories.value = res.data || []
  } catch (e) {
    ElMessage.error('获取分类失败')
  }
}

const openAddDialog = () => {
  isEdit.value = false
  editingId.value = null
  form.value = { name: '', parent_id: null, icon: '', sort_order: 0 }
  dialogVisible.value = true
}

const openEditDialog = (row) => {
  isEdit.value = true
  editingId.value = row.id
  form.value = {
    name: row.name,
    parent_id: row.parent_id || null,
    icon: row.icon || '',
    sort_order: row.sort_order || 0
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!form.value.name) {
    return ElMessage.warning('请输入分类名称')
  }
  submitLoading.value = true
  try {
    if (isEdit.value) {
      await adminAPI.updateCategory(editingId.value, form.value)
      ElMessage.success('分类已更新')
    } else {
      await adminAPI.createCategory(form.value)
      ElMessage.success('分类已创建')
    }
    dialogVisible.value = false
    fetchCategories()
  } catch (e) {
    ElMessage.error(e?.response?.data?.msg || '操作失败')
  } finally {
    submitLoading.value = false
  }
}

const handleDelete = (row) => {
  ElMessageBox.confirm(`确定要删除分类「${row.name}」吗？`, '警告', {
    type: 'warning'
  }).then(async () => {
    try {
      await adminAPI.deleteCategory(row.id)
      ElMessage.success('分类已删除')
      fetchCategories()
    } catch (e) {
      ElMessage.error(e?.response?.data?.msg || '删除失败')
    }
  }).catch(() => {})
}

onMounted(() => {
  fetchCategories()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
