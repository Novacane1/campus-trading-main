<template>
  <div class="order-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-input
              v-model="searchQuery"
              placeholder="搜索商品名称"
              style="width: 200px"
              clearable
              @keyup.enter="handleSearch"
            >
              <template #append>
                <el-button @click="handleSearch">
                  <el-icon><Search /></el-icon>
                </el-button>
              </template>
            </el-input>
            <el-select v-model="filterStatus" placeholder="状态筛选" style="width: 130px; margin-left: 12px" @change="handleSearch">
              <el-option label="全部状态" value="" />
              <el-option label="待支付" value="pending" />
              <el-option label="已支付" value="paid" />
              <el-option label="已发货" value="shipped" />
              <el-option label="已完成" value="completed" />
              <el-option label="已取消" value="cancelled" />
            </el-select>
            <el-checkbox v-model="showAbnormal" style="margin-left: 12px" @change="handleSearch">仅显示异常订单</el-checkbox>
          </div>
        </div>
      </template>

      <el-table :data="orders" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="订单ID" width="120" show-overflow-tooltip />
        <el-table-column label="商品" min-width="200">
          <template #default="scope">
            <div class="item-info">
              <el-image v-if="scope.row.item_image" :src="scope.row.item_image" style="width: 40px; height: 40px; border-radius: 4px" fit="cover" />
              <span class="item-name">{{ scope.row.item_title || '-' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="buyer_name" label="买家" width="100" />
        <el-table-column prop="seller_name" label="卖家" width="100" />
        <el-table-column prop="amount" label="金额" width="100">
          <template #default="scope">¥{{ scope.row.amount }}</template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="scope">
            <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="170" />
        <el-table-column label="操作" fixed="right" width="200">
          <template #default="scope">
            <el-button size="small" @click="viewOrder(scope.row)">详情</el-button>
            <el-button size="small" type="primary" @click="editStatus(scope.row)">修改状态</el-button>
            <el-button v-if="scope.row.status === 'pending'" size="small" type="warning" @click="extendOrder(scope.row)">延期</el-button>
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
          @size-change="fetchOrders"
          @current-change="fetchOrders"
        />
      </div>
    </el-card>

    <!-- 修改状态对话框 -->
    <el-dialog v-model="statusDialogVisible" title="修改订单状态" width="450px">
      <el-form :model="statusForm" label-width="80px">
        <el-form-item label="当前状态">
          <el-tag :type="getStatusType(statusForm.currentStatus)">{{ getStatusText(statusForm.currentStatus) }}</el-tag>
        </el-form-item>
        <el-form-item label="新状态">
          <el-select v-model="statusForm.newStatus" style="width: 100%">
            <el-option label="待支付" value="pending" />
            <el-option label="已支付" value="paid" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
        </el-form-item>
        <el-form-item label="操作原因">
          <el-input v-model="statusForm.reason" type="textarea" :rows="2" placeholder="请输入修改原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="statusDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitStatusChange">确定</el-button>
      </template>
    </el-dialog>

    <!-- 延期对话框 -->
    <el-dialog v-model="extendDialogVisible" title="延长订单有效期" width="400px">
      <el-form :model="extendForm" label-width="80px">
        <el-form-item label="延长时间">
          <el-input-number v-model="extendForm.hours" :min="1" :max="72" /> 小时
        </el-form-item>
        <el-form-item label="原因">
          <el-input v-model="extendForm.reason" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="extendDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitExtend">确定</el-button>
      </template>
    </el-dialog>

    <!-- 订单详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="订单详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="订单ID">{{ orderDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(orderDetail.status)">{{ getStatusText(orderDetail.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="商品名称">{{ orderDetail.item_title }}</el-descriptions-item>
        <el-descriptions-item label="金额">¥{{ orderDetail.amount }}</el-descriptions-item>
        <el-descriptions-item label="买家">{{ orderDetail.buyer_name }}</el-descriptions-item>
        <el-descriptions-item label="卖家">{{ orderDetail.seller_name }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ orderDetail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="过期时间">{{ orderDetail.expire_time || '-' }}</el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import adminAPI from '../../services/adminAPI'

const searchQuery = ref('')
const filterStatus = ref('')
const showAbnormal = ref(false)
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const orders = ref([])
const submitLoading = ref(false)

const statusDialogVisible = ref(false)
const statusForm = ref({ orderId: '', currentStatus: '', newStatus: '', reason: '' })

const extendDialogVisible = ref(false)
const extendForm = ref({ orderId: '', hours: 24, reason: '' })

const detailDialogVisible = ref(false)
const orderDetail = ref({})

const fetchOrders = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getOrders({
      page: currentPage.value,
      limit: pageSize.value,
      search: searchQuery.value || undefined,
      status: filterStatus.value || undefined,
      abnormal: showAbnormal.value ? 'true' : undefined
    })
    orders.value = res.data.orders || []
    total.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('获取订单列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchOrders()
}

const getStatusType = (status) => {
  const map = { pending: 'warning', paid: 'primary', shipped: 'info', completed: 'success', cancelled: 'danger' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { pending: '待支付', paid: '已支付', shipped: '已发货', completed: '已完成', cancelled: '已取消' }
  return map[status] || status
}

const viewOrder = (row) => {
  orderDetail.value = row
  detailDialogVisible.value = true
}

const editStatus = (row) => {
  statusForm.value = { orderId: row.id, currentStatus: row.status, newStatus: row.status, reason: '' }
  statusDialogVisible.value = true
}

const submitStatusChange = async () => {
  if (statusForm.value.newStatus === statusForm.value.currentStatus) {
    ElMessage.warning('状态未改变')
    return
  }
  submitLoading.value = true
  try {
    await adminAPI.updateOrderStatus(statusForm.value.orderId, {
      status: statusForm.value.newStatus,
      reason: statusForm.value.reason
    })
    ElMessage.success('订单状态已更新')
    statusDialogVisible.value = false
    fetchOrders()
  } catch (e) {
    ElMessage.error('更新失败')
  } finally {
    submitLoading.value = false
  }
}

const extendOrder = (row) => {
  extendForm.value = { orderId: row.id, hours: 24, reason: '' }
  extendDialogVisible.value = true
}

const submitExtend = async () => {
  submitLoading.value = true
  try {
    await adminAPI.extendOrderTime(extendForm.value.orderId, {
      hours: extendForm.value.hours,
      reason: extendForm.value.reason
    })
    ElMessage.success('订单有效期已延长')
    extendDialogVisible.value = false
    fetchOrders()
  } catch (e) {
    ElMessage.error('操作失败')
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.header-left { display: flex; align-items: center; }
.pagination-container { margin-top: 24px; display: flex; justify-content: flex-end; }
.item-info { display: flex; align-items: center; gap: 8px; }
.item-name { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
</style>
