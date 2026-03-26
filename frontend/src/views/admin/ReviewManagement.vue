<template>
  <div class="review-management">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-input
              v-model="searchQuery"
              placeholder="搜索评价内容"
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
            <el-select v-model="filterRating" placeholder="评分筛选" style="width: 130px; margin-left: 12px" @change="handleSearch">
              <el-option label="全部评分" value="" />
              <el-option label="5星" :value="5" />
              <el-option label="4星" :value="4" />
              <el-option label="3星" :value="3" />
              <el-option label="2星" :value="2" />
              <el-option label="1星" :value="1" />
            </el-select>
          </div>
        </div>
      </template>

      <el-table :data="reviews" stripe style="width: 100%" v-loading="loading">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column label="评价者" width="120">
          <template #default="scope">
            {{ scope.row.reviewer?.username || '匿名用户' }}
          </template>
        </el-table-column>
        <el-table-column label="商品" width="150">
          <template #default="scope">
            {{ scope.row.item?.name || '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="rating" label="评分" width="120">
          <template #default="scope">
            <el-rate v-model="scope.row.rating" disabled />
          </template>
        </el-table-column>
        <el-table-column prop="content" label="评价内容" min-width="250" show-overflow-tooltip />
        <el-table-column label="回复数" width="80">
          <template #default="scope">
            {{ scope.row.replies?.length || 0 }}
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="评价时间" width="170" />
        <el-table-column label="操作" fixed="right" width="150">
          <template #default="scope">
            <el-button size="small" @click="viewReview(scope.row)">详情</el-button>
            <el-button size="small" type="danger" @click="deleteReview(scope.row)">删除</el-button>
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
          @size-change="fetchReviews"
          @current-change="fetchReviews"
        />
      </div>
    </el-card>

    <!-- 评价详情对话框 -->
    <el-dialog v-model="detailDialogVisible" title="评价详情" width="600px">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="评价ID">{{ reviewDetail.id }}</el-descriptions-item>
        <el-descriptions-item label="评分">
          <el-rate v-model="reviewDetail.rating" disabled />
        </el-descriptions-item>
        <el-descriptions-item label="评价者">{{ reviewDetail.reviewer?.username || '匿名用户' }}</el-descriptions-item>
        <el-descriptions-item label="商品">{{ reviewDetail.item?.name || '-' }}</el-descriptions-item>
        <el-descriptions-item label="评价时间" :span="2">{{ reviewDetail.created_at }}</el-descriptions-item>
        <el-descriptions-item label="评价内容" :span="2">{{ reviewDetail.content }}</el-descriptions-item>
      </el-descriptions>

      <div v-if="reviewDetail.replies?.length" class="replies-section">
        <h4>回复列表 ({{ reviewDetail.replies.length }})</h4>
        <div v-for="reply in reviewDetail.replies" :key="reply.id" class="reply-item">
          <div class="reply-header">
            <span class="reply-user">{{ reply.reviewer?.username || '匿名用户' }}</span>
            <span class="reply-time">{{ reply.created_at }}</span>
            <el-button size="small" type="danger" @click="deleteReplyItem(reply)">删除</el-button>
          </div>
          <div class="reply-content">{{ reply.content }}</div>
        </div>
      </div>
    </el-dialog>

    <!-- 删除确认对话框 -->
    <el-dialog v-model="deleteDialogVisible" title="删除评价" width="400px">
      <el-form :model="deleteForm" label-width="80px">
        <el-form-item label="删除原因">
          <el-input v-model="deleteForm.reason" type="textarea" :rows="3" placeholder="请输入删除原因" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" :loading="submitLoading" @click="confirmDelete">确认删除</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import adminAPI from '../../services/adminAPI'

const searchQuery = ref('')
const filterRating = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)
const loading = ref(false)
const reviews = ref([])
const submitLoading = ref(false)

const detailDialogVisible = ref(false)
const reviewDetail = ref({})

const deleteDialogVisible = ref(false)
const deleteForm = ref({ reviewId: null, reason: '' })

const fetchReviews = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getReviews({
      page: currentPage.value,
      limit: pageSize.value,
      search: searchQuery.value || undefined,
      rating: filterRating.value || undefined
    })
    reviews.value = res.data.reviews || []
    total.value = res.data.total || 0
  } catch (e) {
    ElMessage.error('获取评价列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchReviews()
}

const viewReview = (row) => {
  reviewDetail.value = row
  detailDialogVisible.value = true
}

const deleteReview = (row) => {
  deleteForm.value = { reviewId: row.id, reason: '' }
  deleteDialogVisible.value = true
}

const confirmDelete = async () => {
  submitLoading.value = true
  try {
    await adminAPI.deleteReview(deleteForm.value.reviewId, { reason: deleteForm.value.reason })
    ElMessage.success('评价已删除')
    deleteDialogVisible.value = false
    detailDialogVisible.value = false
    fetchReviews()
  } catch (e) {
    ElMessage.error('删除失败')
  } finally {
    submitLoading.value = false
  }
}

const deleteReplyItem = async (reply) => {
  try {
    await adminAPI.deleteReview(reply.id, { reason: '管理员删除回复' })
    ElMessage.success('回复已删除')
    reviewDetail.value.replies = reviewDetail.value.replies.filter(r => r.id !== reply.id)
  } catch (e) {
    ElMessage.error('删除失败')
  }
}

onMounted(() => {
  fetchReviews()
})
</script>

<style scoped>
.card-header { display: flex; justify-content: space-between; align-items: center; }
.pagination-container { margin-top: 24px; display: flex; justify-content: flex-end; }
.replies-section { margin-top: 20px; }
.replies-section h4 { margin-bottom: 12px; color: #333; }
.reply-item { padding: 12px; background: #f5f7fa; border-radius: 4px; margin-bottom: 8px; }
.reply-header { display: flex; align-items: center; gap: 12px; margin-bottom: 8px; }
.reply-user { font-weight: 500; }
.reply-time { color: #999; font-size: 12px; flex: 1; }
.reply-content { color: #666; line-height: 1.6; }
</style>
