<template>
  <div class="product-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-input
              v-model="searchQuery"
              placeholder="搜索商品标题/分类"
              style="width: 300px"
              clearable
            >
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
            <el-select v-model="filterStatus" placeholder="状态筛选" style="width: 150px; margin-left: 12px">
              <el-option label="全部状态" value="" />
              <el-option label="在售" value="on_sale" />
              <el-option label="已售" value="sold" />
              <el-option label="已锁定" value="locked" />
            </el-select>
          </div>
          <div class="header-right">
            <el-button type="danger" :disabled="!selectedProducts.length" @click="batchOffShelf">批量下架</el-button>
          </div>
        </div>
      </template>

      <el-table
        :data="products"
        stripe
        style="width: 100%"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="商品图" width="100">
          <template #default="scope">
            <el-image
              style="width: 50px; height: 50px; border-radius: 4px"
              :src="scope.row.image"
              :preview-src-list="[scope.row.image]"
              fit="cover"
            />
          </template>
        </el-table-column>
        <el-table-column prop="title" label="商品名称" min-width="200" show-overflow-tooltip />
        <el-table-column prop="category" label="分类" width="120" />
        <el-table-column prop="price" label="价格" width="100" sortable>
          <template #default="scope">¥{{ scope.row.price }}</template>
        </el-table-column>
        <el-table-column prop="seller" label="卖家" width="120" />
        <el-table-column prop="status" label="状态" width="120">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="createTime" label="发布时间" width="180" sortable />
        <el-table-column label="操作" fixed="right" width="250">
          <template #default="scope">
            <el-button v-if="scope.row.status === 'locked'" size="small" type="success" @click="approveProduct(scope.row)">审核</el-button>
            <el-button size="small" type="primary" @click="editProduct(scope.row)">编辑</el-button>
            <el-button size="small" @click="viewDetails(scope.row)">详情</el-button>
            <el-button size="small" type="danger" @click="removeProduct(scope.row)">下架</el-button>
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

    <!-- 编辑商品对话框 -->
    <el-dialog v-model="editDialogVisible" title="编辑商品" width="520px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="商品名称">
          <el-input v-model="editForm.name" />
        </el-form-item>
        <el-form-item label="价格">
          <el-input-number v-model="editForm.price" :min="0" :precision="2" :step="1" />
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="editForm.status">
            <el-option label="在售" value="on_sale" />
            <el-option label="已锁定" value="locked" />
            <el-option label="已删除" value="deleted" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="editForm.description" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="editLoading" @click="submitEditProduct">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import adminAPI from '../../services/adminAPI'
import productAPI from '../../services/productAPI'

const searchQuery = ref('')
const filterStatus = ref('')
const selectedProducts = ref([])
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const products = ref([])
const editDialogVisible = ref(false)
const editLoading = ref(false)
const editForm = ref({ id: null, name: '', price: 0, status: '', description: '' })

const fetchProducts = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getProducts({
      page: currentPage.value,
      per_page: pageSize.value,
      search: searchQuery.value || undefined,
      status: filterStatus.value || undefined
    })
    const data = res.data
    products.value = (data.products || []).map(p => ({
      id: p.id,
      title: p.name,
      category: p.category_id || '-',
      price: p.price,
      seller: p.seller?.username || '-',
      status: p.status,
      description: p.description || '',
      createTime: p.created_at,
      image: p.images?.[0] || ''
    }))
    total.value = data.total || 0
  } catch (e) {
    ElMessage.error('获取商品列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchProducts()
}

const handleSelectionChange = (val) => {
  selectedProducts.value = val
}

const getStatusType = (status) => {
  const map = { 'on_sale': 'success', 'sold': 'info', 'locked': 'warning', 'deleted': 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { 'on_sale': '在售', 'sold': '已售', 'locked': '已锁定', 'deleted': '已删除' }
  return map[status] || status
}

const approveProduct = async (row) => {
  try {
    await adminAPI.approveProduct(row.id)
    ElMessage.success(`商品 "${row.title}" 已审核通过`)
    fetchProducts()
  } catch (e) {
    ElMessage.error('审核失败')
  }
}

const viewDetails = (row) => {
  window.open(`/product/${row.id}`, '_blank')
}

const editProduct = (row) => {
  editForm.value = {
    id: row.id,
    name: row.title,
    price: row.price,
    status: row.status,
    description: row.description || ''
  }
  editDialogVisible.value = true
}

const submitEditProduct = async () => {
  editLoading.value = true
  try {
    await productAPI.updateProduct(editForm.value.id, {
      name: editForm.value.name,
      price: editForm.value.price,
      description: editForm.value.description
    })
    if (editForm.value.status === 'on_sale') {
      await adminAPI.approveProduct(editForm.value.id)
    } else if (editForm.value.status === 'deleted') {
      await adminAPI.rejectProduct(editForm.value.id, '管理员操作')
    }
    ElMessage.success('商品信息已更新')
    editDialogVisible.value = false
    fetchProducts()
  } catch (e) {
    ElMessage.error('更新失败')
  } finally {
    editLoading.value = false
  }
}

const removeProduct = (row) => {
  ElMessageBox.confirm(`确定要下架商品 "${row.title}" 吗？`, '警告', {
    type: 'warning'
  }).then(async () => {
    try {
      await adminAPI.rejectProduct(row.id, '管理员下架')
      ElMessage.success('下架成功')
      fetchProducts()
    } catch (e) {
      ElMessage.error('操作失败')
    }
  }).catch(() => {})
}

const batchOffShelf = () => {
  ElMessageBox.confirm(`确定要批量下架 ${selectedProducts.value.length} 个商品吗？`, '警告', {
    type: 'warning'
  }).then(async () => {
    try {
      await Promise.all(selectedProducts.value.map(p => adminAPI.rejectProduct(p.id, '管理员批量下架')))
      ElMessage.success('批量下架成功')
      fetchProducts()
    } catch (e) {
      ElMessage.error('部分商品下架失败')
      fetchProducts()
    }
  }).catch(() => {})
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchProducts()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchProducts()
}

onMounted(() => {
  fetchProducts()
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
