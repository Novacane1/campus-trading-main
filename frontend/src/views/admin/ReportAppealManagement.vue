<template>
  <div class="report-appeal-management">
    <el-tabs v-model="activeTab" @tab-change="handleTabChange">
      <el-tab-pane label="举报管理" name="reports">
        <el-card>
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-select v-model="reportStatus" placeholder="状态筛选" style="width: 130px" @change="fetchReports">
                  <el-option label="全部状态" value="" />
                  <el-option label="待处理" value="pending" />
                  <el-option label="处理中" value="processing" />
                  <el-option label="已解决" value="resolved" />
                  <el-option label="已驳回" value="rejected" />
                </el-select>
                <el-select v-model="reportType" placeholder="类型筛选" style="width: 130px; margin-left: 12px" @change="fetchReports">
                  <el-option label="全部类型" value="" />
                  <el-option label="用户" value="user" />
                  <el-option label="商品" value="item" />
                  <el-option label="评价" value="review" />
                  <el-option label="订单" value="order" />
                </el-select>
              </div>
            </div>
          </template>

          <el-table :data="reports" stripe style="width: 100%" v-loading="reportLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="reporter_name" label="举报人" width="100" />
            <el-table-column prop="report_type" label="类型" width="80">
              <template #default="scope">
                <el-tag size="small">{{ getReportTypeText(scope.row.report_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="举报原因" width="120">
              <template #default="scope">{{ getReasonText(scope.row.reason) }}</template>
            </el-table-column>
            <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">{{ getStatusText(scope.row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="举报时间" width="170" />
            <el-table-column label="操作" fixed="right" width="150">
              <template #default="scope">
                <el-button size="small" @click="viewReport(scope.row)">详情</el-button>
                <el-button v-if="scope.row.status === 'pending'" size="small" type="primary" @click="handleReport(scope.row)">处理</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="reportPage"
              v-model:page-size="reportPageSize"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              :total="reportTotal"
              @size-change="fetchReports"
              @current-change="fetchReports"
            />
          </div>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="申诉管理" name="appeals">
        <el-card>
          <template #header>
            <div class="card-header">
              <div class="header-left">
                <el-select v-model="appealStatus" placeholder="状态筛选" style="width: 130px" @change="fetchAppeals">
                  <el-option label="全部状态" value="" />
                  <el-option label="待处理" value="pending" />
                  <el-option label="处理中" value="processing" />
                  <el-option label="已通过" value="approved" />
                  <el-option label="已驳回" value="rejected" />
                </el-select>
                <el-select v-model="appealType" placeholder="类型筛选" style="width: 130px; margin-left: 12px" @change="fetchAppeals">
                  <el-option label="全部类型" value="" />
                  <el-option label="订单" value="order" />
                  <el-option label="评价" value="review" />
                  <el-option label="封禁" value="ban" />
                  <el-option label="商品" value="item" />
                </el-select>
              </div>
            </div>
          </template>

          <el-table :data="appeals" stripe style="width: 100%" v-loading="appealLoading">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="appellant_name" label="申诉人" width="100" />
            <el-table-column prop="appeal_type" label="类型" width="80">
              <template #default="scope">
                <el-tag size="small">{{ getAppealTypeText(scope.row.appeal_type) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="申诉理由" min-width="250" show-overflow-tooltip />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="scope">
                <el-tag :type="getAppealStatusType(scope.row.status)">{{ getAppealStatusText(scope.row.status) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="申诉时间" width="170" />
            <el-table-column label="操作" fixed="right" width="150">
              <template #default="scope">
                <el-button size="small" @click="viewAppeal(scope.row)">详情</el-button>
                <el-button v-if="scope.row.status === 'pending'" size="small" type="primary" @click="handleAppeal(scope.row)">处理</el-button>
              </template>
            </el-table-column>
          </el-table>

          <div class="pagination-container">
            <el-pagination
              v-model:current-page="appealPage"
              v-model:page-size="appealPageSize"
              :page-sizes="[10, 20, 50]"
              layout="total, sizes, prev, pager, next"
              :total="appealTotal"
              @size-change="fetchAppeals"
              @current-change="fetchAppeals"
            />
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 举报详情/处理对话框 -->
    <el-dialog v-model="reportDialogVisible" :title="isHandling ? '处理举报' : '举报详情'" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="举报ID">{{ currentReport.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getStatusType(currentReport.status)">{{ getStatusText(currentReport.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="举报人">{{ currentReport.reporter_name }}</el-descriptions-item>
        <el-descriptions-item label="举报类型">{{ getReportTypeText(currentReport.report_type) }}</el-descriptions-item>
        <el-descriptions-item label="举报原因">{{ getReasonText(currentReport.reason) }}</el-descriptions-item>
        <el-descriptions-item label="举报时间">{{ currentReport.created_at }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ currentReport.description || '-' }}</el-descriptions-item>
      </el-descriptions>

      <div v-if="currentReport.evidence_images?.length" class="evidence-section">
        <h4>证据图片</h4>
        <el-image v-for="(img, idx) in currentReport.evidence_images" :key="idx" :src="img" style="width: 100px; height: 100px; margin-right: 8px" fit="cover" :preview-src-list="currentReport.evidence_images" />
      </div>

      <div v-if="isHandling" class="handle-section">
        <el-divider />
        <el-form :model="handleForm" label-width="80px">
          <el-form-item label="处理结果">
            <el-radio-group v-model="handleForm.action">
              <el-radio value="resolve">确认违规</el-radio>
              <el-radio value="reject">驳回举报</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="处理说明">
            <el-input v-model="handleForm.result" type="textarea" :rows="3" placeholder="请输入处理说明" />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="reportDialogVisible = false">关闭</el-button>
        <el-button v-if="isHandling" type="primary" :loading="submitLoading" @click="submitReportHandle">提交</el-button>
      </template>
    </el-dialog>

    <!-- 申诉详情/处理对话框 -->
    <el-dialog v-model="appealDialogVisible" :title="isAppealHandling ? '处理申诉' : '申诉详情'" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="申诉ID">{{ currentAppeal.id }}</el-descriptions-item>
        <el-descriptions-item label="状态">
          <el-tag :type="getAppealStatusType(currentAppeal.status)">{{ getAppealStatusText(currentAppeal.status) }}</el-tag>
        </el-descriptions-item>
        <el-descriptions-item label="申诉人">{{ currentAppeal.appellant_name }}</el-descriptions-item>
        <el-descriptions-item label="申诉类型">{{ getAppealTypeText(currentAppeal.appeal_type) }}</el-descriptions-item>
        <el-descriptions-item label="申诉时间">{{ currentAppeal.created_at }}</el-descriptions-item>
        <el-descriptions-item label="目标ID">{{ currentAppeal.target_id }}</el-descriptions-item>
        <el-descriptions-item label="申诉理由" :span="2">{{ currentAppeal.reason }}</el-descriptions-item>
      </el-descriptions>

      <div v-if="currentAppeal.evidence_images?.length" class="evidence-section">
        <h4>证据图片</h4>
        <el-image v-for="(img, idx) in currentAppeal.evidence_images" :key="idx" :src="img" style="width: 100px; height: 100px; margin-right: 8px" fit="cover" :preview-src-list="currentAppeal.evidence_images" />
      </div>

      <div v-if="isAppealHandling" class="handle-section">
        <el-divider />
        <el-form :model="appealHandleForm" label-width="80px">
          <el-form-item label="处理结果">
            <el-radio-group v-model="appealHandleForm.action">
              <el-radio value="approve">通过申诉</el-radio>
              <el-radio value="reject">驳回申诉</el-radio>
            </el-radio-group>
          </el-form-item>
          <el-form-item label="处理说明">
            <el-input v-model="appealHandleForm.result" type="textarea" :rows="3" placeholder="请输入处理说明" />
          </el-form-item>
        </el-form>
      </div>

      <template #footer>
        <el-button @click="appealDialogVisible = false">关闭</el-button>
        <el-button v-if="isAppealHandling" type="primary" :loading="submitLoading" @click="submitAppealHandle">提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import adminAPI from '../../services/adminAPI'

const activeTab = ref('reports')

// 举报相关
const reportStatus = ref('')
const reportType = ref('')
const reportPage = ref(1)
const reportPageSize = ref(10)
const reportTotal = ref(0)
const reportLoading = ref(false)
const reports = ref([])

// 申诉相关
const appealStatus = ref('')
const appealType = ref('')
const appealPage = ref(1)
const appealPageSize = ref(10)
const appealTotal = ref(0)
const appealLoading = ref(false)
const appeals = ref([])

const submitLoading = ref(false)

// 举报对话框
const reportDialogVisible = ref(false)
const isHandling = ref(false)
const currentReport = ref({})
const handleForm = ref({ action: 'resolve', result: '' })

// 申诉对话框
const appealDialogVisible = ref(false)
const isAppealHandling = ref(false)
const currentAppeal = ref({})
const appealHandleForm = ref({ action: 'approve', result: '' })

const fetchReports = async () => {
  reportLoading.value = true
  try {
    const res = await adminAPI.getReports({
      page: reportPage.value,
      limit: reportPageSize.value,
      status: reportStatus.value || undefined,
      type: reportType.value || undefined
    })
    reports.value = res.data.reports || []
    reportTotal.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('获取举报列表失败')
  } finally {
    reportLoading.value = false
  }
}

const fetchAppeals = async () => {
  appealLoading.value = true
  try {
    const res = await adminAPI.getAppeals({
      page: appealPage.value,
      limit: appealPageSize.value,
      status: appealStatus.value || undefined,
      type: appealType.value || undefined
    })
    appeals.value = res.data.appeals || []
    appealTotal.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('获取申诉列表失败')
  } finally {
    appealLoading.value = false
  }
}

const handleTabChange = (tab) => {
  if (tab === 'reports') fetchReports()
  else fetchAppeals()
}

const getReportTypeText = (type) => {
  const map = { user: '用户', item: '商品', review: '评价', order: '订单' }
  return map[type] || type
}

const getReasonText = (reason) => {
  const map = { fraud: '欺诈', spam: '垃圾信息', inappropriate: '不当内容', fake: '虚假信息', other: '其他' }
  return map[reason] || reason
}

const getStatusType = (status) => {
  const map = { pending: 'warning', processing: 'primary', resolved: 'success', rejected: 'info' }
  return map[status] || 'info'
}

const getStatusText = (status) => {
  const map = { pending: '待处理', processing: '处理中', resolved: '已解决', rejected: '已驳回' }
  return map[status] || status
}

const getAppealTypeText = (type) => {
  const map = { order: '订单', review: '评价', ban: '封禁', item: '商品' }
  return map[type] || type
}

const getAppealStatusType = (status) => {
  const map = { pending: 'warning', processing: 'primary', approved: 'success', rejected: 'danger' }
  return map[status] || 'info'
}

const getAppealStatusText = (status) => {
  const map = { pending: '待处理', processing: '处理中', approved: '已通过', rejected: '已驳回' }
  return map[status] || status
}

const viewReport = (row) => {
  currentReport.value = row
  isHandling.value = false
  reportDialogVisible.value = true
}

const handleReport = (row) => {
  currentReport.value = row
  isHandling.value = true
  handleForm.value = { action: 'resolve', result: '' }
  reportDialogVisible.value = true
}

const submitReportHandle = async () => {
  submitLoading.value = true
  try {
    await adminAPI.handleReport(currentReport.value.id, handleForm.value)
    ElMessage.success('举报已处理')
    reportDialogVisible.value = false
    fetchReports()
  } catch (e) {
    ElMessage.error('处理失败')
  } finally {
    submitLoading.value = false
  }
}

const viewAppeal = (row) => {
  currentAppeal.value = row
  isAppealHandling.value = false
  appealDialogVisible.value = true
}

const handleAppeal = (row) => {
  currentAppeal.value = row
  isAppealHandling.value = true
  appealHandleForm.value = { action: 'approve', result: '' }
  appealDialogVisible.value = true
}

const submitAppealHandle = async () => {
  submitLoading.value = true
  try {
    await adminAPI.handleAppeal(currentAppeal.value.id, appealHandleForm.value)
    ElMessage.success('申诉已处理')
    appealDialogVisible.value = false
    fetchAppeals()
  } catch (e) {
    ElMessage.error('处理失败')
  } finally {
    submitLoading.value = false
  }
}

onMounted(() => {
  fetchReports()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.pagination-container { margin-top: 24px; display: flex; justify-content: flex-end; }
.evidence-section { margin-top: 16px; }
.evidence-section h4 { margin-bottom: 8px; color: #333; }
.handle-section { margin-top: 16px; }
</style>
