<template>
  <div class="review-section">
    <div class="review-header">
      <h3>商品评价</h3>
      <div class="rating-summary" v-if="reviews.length > 0">
        <el-rate v-model="avgRating" disabled show-score text-color="var(--warning-color)" />
        <span class="review-count">{{ reviews.length }} 条评价</span>
      </div>
    </div>

    <!-- 发表评价区域 -->
    <div v-if="isLoggedIn" class="post-review-section">
      <div class="post-review-header">
        <span class="post-review-title">发表评价</span>
      </div>
      <div class="post-review-form">
        <div class="form-row" v-if="reviewableOrders.length > 0">
          <span class="form-label">关联订单：</span>
          <el-select v-model="newReview.order_id" placeholder="选择订单（可选）" size="default" style="flex:1" clearable>
            <el-option
              v-for="o in reviewableOrders"
              :key="o.order_id"
              :label="`订单 ${o.order_id.substring(0, 8)}... (${o.created_at ? new Date(o.created_at).toLocaleDateString('zh-CN') : ''})`"
              :value="o.order_id"
            />
          </el-select>
        </div>
        <div class="form-row">
          <span class="form-label">评分：</span>
          <el-rate v-model="newReview.rating" show-text :texts="['很差', '较差', '一般', '满意', '非常满意']" />
        </div>
        <el-input
          v-model="newReview.content"
          type="textarea"
          :rows="3"
          placeholder="写下你的评价..."
          maxlength="500"
          show-word-limit
        />
        <div class="form-actions">
          <el-checkbox v-model="newReview.is_anonymous" label="匿名评价" size="small" />
          <el-button
            type="primary"
            size="default"
            @click="submitNewReview"
            :loading="submitLoading"
            :disabled="newReview.rating < 1"
          >
            提交评价
          </el-button>
        </div>
      </div>
    </div>

    <div v-if="reviews.length === 0" class="no-reviews">
      <el-empty description="暂无评价" :image-size="80" />
    </div>

    <div v-else class="review-list">
      <div v-for="review in reviews" :key="review.id" class="review-item">
        <div class="review-user">
          <div class="review-avatar">
            {{ review.reviewer?.username?.charAt(0).toUpperCase() || 'U' }}
          </div>
          <div class="user-info">
            <span class="username">{{ review.reviewer?.username || '匿名用户' }}</span>
            <span class="review-time">{{ formatTime(review.created_at) }}</span>
          </div>
        </div>
        <div class="review-rating" v-if="review.rating">
          <el-rate v-model="review.rating" disabled size="small" />
        </div>
        <div class="review-content" v-if="review.content">
          {{ review.content }}
        </div>
        <div class="review-content empty" v-else>
          用户未填写评价内容
        </div>

        <!-- 回复列表 -->
        <div class="replies-section" v-if="review.replies && review.replies.length > 0">
          <div class="replies-toggle" @click="toggleReplies(review.id)">
            <el-icon><ChatLineRound /></el-icon>
            <span>{{ expandedReplies[review.id] ? '收起' : '展开' }} {{ review.replies.length }} 条回复</span>
          </div>
          <transition name="fade">
            <div v-if="expandedReplies[review.id]" class="replies-list">
              <div v-for="reply in review.replies" :key="reply.id" class="reply-item">
                <div class="reply-user">
                  <div class="reply-avatar">
                    {{ reply.reviewer?.username?.charAt(0).toUpperCase() || 'U' }}
                  </div>
                  <div class="reply-info">
                    <span class="reply-username">{{ reply.reviewer?.username || '匿名用户' }}</span>
                    <span class="reply-time">{{ formatTime(reply.created_at) }}</span>
                  </div>
                </div>
                <div class="reply-content">{{ reply.content }}</div>
              </div>
            </div>
          </transition>
        </div>

        <!-- 回复输入 -->
        <div class="reply-action" v-if="isLoggedIn">
          <span class="reply-trigger" @click="toggleReplyInput(review.id)" v-if="!replyInputs[review.id]">
            <el-icon><ChatLineRound /></el-icon> 回复
          </span>
          <div v-if="replyInputs[review.id]" class="reply-input-area">
            <el-input
              v-model="replyContents[review.id]"
              type="textarea"
              :rows="2"
              placeholder="写下你的回复..."
              maxlength="300"
              show-word-limit
              size="small"
            />
            <div class="reply-input-actions">
              <el-button size="small" @click="toggleReplyInput(review.id)">取消</el-button>
              <el-button
                size="small"
                type="primary"
                @click="submitReply(review.id)"
                :loading="replyLoading[review.id]"
                :disabled="!replyContents[review.id]?.trim()"
              >
                发送
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, reactive } from 'vue'
import { ChatLineRound } from '@element-plus/icons-vue'
import { useUserStore } from '@/stores/user'
import { getItemReviews, replyToReview, getReviewableOrders, createReview } from '@/services/reviewAPI'
import { ElMessage } from 'element-plus'

const props = defineProps({
  itemId: {
    type: [Number, String],
    required: true
  }
})

const userStore = useUserStore()
const isLoggedIn = computed(() => userStore.isLoggedIn)

const reviews = ref([])
const loading = ref(false)
const expandedReplies = reactive({})
const replyInputs = reactive({})
const replyContents = reactive({})
const replyLoading = reactive({})

// 发表评价相关
const reviewableOrders = ref([])
const submitLoading = ref(false)
const newReview = reactive({
  order_id: '',
  rating: 5,
  content: '',
  is_anonymous: false
})

const avgRating = computed(() => {
  const ratedReviews = reviews.value.filter(r => r.rating)
  if (ratedReviews.length === 0) return 0
  const sum = ratedReviews.reduce((acc, r) => acc + r.rating, 0)
  return Math.round((sum / ratedReviews.length) * 10) / 10
})

const formatTime = (timeStr) => {
  if (!timeStr) return ''
  const date = new Date(timeStr)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  })
}

const toggleReplies = (reviewId) => {
  expandedReplies[reviewId] = !expandedReplies[reviewId]
}

const toggleReplyInput = (reviewId) => {
  replyInputs[reviewId] = !replyInputs[reviewId]
  if (!replyInputs[reviewId]) {
    replyContents[reviewId] = ''
  }
}

const submitReply = async (reviewId) => {
  const content = replyContents[reviewId]?.trim()
  if (!content) return

  replyLoading[reviewId] = true
  try {
    const res = await replyToReview({ parent_id: reviewId, content })
    // 把新回复追加到对应评价的 replies 列表
    const review = reviews.value.find(r => r.id === reviewId)
    if (review) {
      if (!review.replies) review.replies = []
      review.replies.push(res.data.reply)
      expandedReplies[reviewId] = true
    }
    replyContents[reviewId] = ''
    replyInputs[reviewId] = false
    ElMessage.success('回复成功')
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '回复失败')
  } finally {
    replyLoading[reviewId] = false
  }
}

const submitNewReview = async () => {
  if (newReview.rating < 1) return
  submitLoading.value = true
  try {
    const payload = {
      rating: newReview.rating,
      content: newReview.content,
      is_anonymous: newReview.is_anonymous
    }
    if (newReview.order_id) {
      payload.order_id = newReview.order_id
    } else {
      payload.item_id = props.itemId
    }
    await createReview(payload)
    ElMessage.success('评价成功')
    newReview.order_id = ''
    newReview.rating = 5
    newReview.content = ''
    newReview.is_anonymous = false
    // 刷新评价列表和可评价订单
    await loadReviews()
    await loadReviewableOrders()
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '评价失败')
  } finally {
    submitLoading.value = false
  }
}

const loadReviews = async () => {
  loading.value = true
  try {
    const response = await getItemReviews(props.itemId)
    reviews.value = response.data || []
  } catch (error) {
    console.error('加载评价失败:', error)
  } finally {
    loading.value = false
  }
}

const loadReviewableOrders = async () => {
  if (!isLoggedIn.value) return
  try {
    const res = await getReviewableOrders(props.itemId)
    reviewableOrders.value = res.data || []
  } catch {
    reviewableOrders.value = []
  }
}

onMounted(() => {
  loadReviews()
  loadReviewableOrders()
})
</script>

<style scoped>
.review-section {
  padding: 16px 0;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.review-header h3 {
  margin: 0;
  font-size: 16px;
  color: var(--text-primary);
}

.rating-summary {
  display: flex;
  align-items: center;
  gap: 12px;
}

.review-count {
  color: var(--text-tertiary);
  font-size: 13px;
}

.no-reviews {
  padding: 20px 0;
}

.review-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.review-item {
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  transition: box-shadow 0.2s;
}

.review-item:hover {
  box-shadow: var(--shadow-sm);
}

.review-user {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.review-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.username {
  font-size: 14px;
  color: var(--text-primary);
  font-weight: 500;
}

.review-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.review-rating {
  margin-bottom: 8px;
}

.review-content {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
}

.review-content.empty {
  color: var(--text-quaternary);
  font-style: italic;
}

/* 回复区域 */
.replies-section {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border-secondary);
}

.replies-toggle {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: var(--primary-color);
  cursor: pointer;
  user-select: none;
  transition: opacity 0.2s;
}

.replies-toggle:hover {
  opacity: 0.8;
}

.replies-list {
  margin-top: 10px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.reply-item {
  padding: 10px 12px;
  background: var(--bg-primary);
  border-radius: 8px;
  border-left: 3px solid var(--primary-color);
}

.reply-user {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.reply-avatar {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--success-color, #67c23a);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 11px;
  font-weight: 600;
  flex-shrink: 0;
}

.reply-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.reply-username {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.reply-time {
  font-size: 11px;
  color: var(--text-tertiary);
}

.reply-content {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.5;
}

/* 回复输入 */
.reply-action {
  margin-top: 10px;
}

.reply-trigger {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: var(--text-tertiary);
  cursor: pointer;
  transition: color 0.2s;
}

.reply-trigger:hover {
  color: var(--primary-color);
}

.reply-input-area {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.reply-input-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

/* 发表评价区域 */
.post-review-section {
  margin-bottom: 20px;
  padding: 16px;
  background: var(--bg-secondary);
  border-radius: 12px;
  border: 1px dashed var(--border-primary);
}

.post-review-header {
  margin-bottom: 12px;
}

.post-review-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.post-review-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.form-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.form-label {
  font-size: 13px;
  color: var(--text-secondary);
  white-space: nowrap;
}

.form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
