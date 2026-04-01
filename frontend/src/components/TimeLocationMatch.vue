<template>
  <div class="time-location-match">
    <el-card class="match-card">
      <template #header>
        <div class="card-header">
          <div>
            <div class="card-title">推荐面交方案</div>
            <div class="card-subtitle">基于双方时间与地点偏好自动生成</div>
          </div>
          <el-tag :type="matchScoreType" size="large">
            {{ matchScore }}分
          </el-tag>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>正在生成推荐面交方案...</span>
      </div>

      <div v-else-if="matchData">
        <el-alert
          :title="matchData.message"
          :type="matchData.has_match ? 'success' : 'warning'"
          :closable="false"
          show-icon
          class="match-alert"
        />

        <div v-if="showProfileTips" class="profile-tip-box">
          <div class="profile-tip-title">你的交易偏好还不完整</div>
          <ul class="profile-tip-list">
            <li v-for="tip in matchData.profile_completion_tips" :key="tip">{{ tip }}</li>
          </ul>
          <el-button type="primary" link @click="goProfile">去完善偏好</el-button>
        </div>

        <div v-if="isActionable" class="plan-card">
          <div class="plan-badge">
            {{ matchData.exact_match ? '直接可约' : '优先协商' }}
          </div>
          <div class="plan-grid">
            <div class="plan-item">
              <div class="plan-label">推荐时间</div>
              <div class="plan-value">
                {{ matchData.best_time_label || '暂无明确推荐时间' }}
              </div>
              <div class="plan-reason" v-if="matchData.best_time_reason">
                {{ matchData.best_time_reason }}
              </div>
            </div>
            <div class="plan-item">
              <div class="plan-label">推荐地点</div>
              <div class="plan-value">
                {{ matchData.best_location || '暂无明确推荐地点' }}
              </div>
              <div class="plan-reason" v-if="matchData.best_location_reason">
                {{ matchData.best_location_reason }}
              </div>
            </div>
          </div>
          <div class="plan-summary">{{ matchData.action_plan }}</div>
          <div class="plan-actions">
            <el-button type="primary" :loading="sending" @click="sendRecommendation">
              一键发给卖家
            </el-button>
            <el-button @click="openChat">进入聊天</el-button>
            <el-button plain @click="copyRecommendation">复制方案</el-button>
          </div>
        </div>

        <div
          v-if="matchData.common_time_slots && matchData.common_time_slots.length > 0"
          class="match-section"
        >
          <h4>共同可交易时间</h4>
          <el-space wrap>
            <el-tag
              v-for="slot in matchData.common_time_slots"
              :key="slot"
              type="success"
              effect="plain"
            >
              {{ slot }}
            </el-tag>
          </el-space>
        </div>

        <div
          v-if="matchData.common_locations && matchData.common_locations.length > 0"
          class="match-section"
        >
          <h4>共同可接受地点</h4>
          <el-space wrap>
            <el-tag
              v-for="location in matchData.common_locations"
              :key="location"
              type="success"
              effect="plain"
            >
              {{ location }}
            </el-tag>
          </el-space>
        </div>

        <div
          v-if="matchData.time_candidates && matchData.time_candidates.length > 0"
          class="match-section"
        >
          <h4>可优先尝试的时间</h4>
          <div class="candidate-list">
            <div
              v-for="candidate in matchData.time_candidates"
              :key="candidate.label"
              class="candidate-card"
            >
              <div class="candidate-main">
                <span class="candidate-label">{{ candidate.label }}</span>
                <el-tag size="small" :type="candidate.exact_match ? 'success' : 'warning'">
                  {{ candidate.score }}分
                </el-tag>
              </div>
              <div class="candidate-reason">{{ candidate.reason }}</div>
            </div>
          </div>
        </div>

        <div
          v-if="matchData.location_candidates && matchData.location_candidates.length > 0"
          class="match-section"
        >
          <h4>可优先尝试的地点</h4>
          <div class="candidate-list">
            <div
              v-for="candidate in matchData.location_candidates"
              :key="candidate.location"
              class="candidate-card"
            >
              <div class="candidate-main">
                <span class="candidate-label">{{ candidate.location }}</span>
                <el-tag size="small" :type="candidate.exact_match ? 'success' : 'info'">
                  {{ candidate.score }}分
                </el-tag>
              </div>
              <div class="candidate-reason">{{ candidate.reason }}</div>
            </div>
          </div>
        </div>

        <div v-if="!isActionable" class="no-match-tips">
          <el-divider />
          <p>当前还不能直接给出明确面交方案：</p>
          <ul>
            <li>建议先补充个人中心里的常用交易时间和地点</li>
            <li>也可以先联系卖家，确认对方更方便的时间和公共地点</li>
            <li>优先选择图书馆、食堂、校门口等公共区域面交</li>
          </ul>
          <div class="plan-actions">
            <el-button type="primary" @click="openChat">联系卖家协商</el-button>
            <el-button plain @click="goProfile">完善偏好</el-button>
          </div>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { calculateMatch } from '@/services/timeLocationAPI'
import chatAPI from '@/services/chatAPI'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  itemId: {
    type: Number,
    required: true
  },
  sellerId: {
    type: [Number, String],
    default: null
  },
  sellerName: {
    type: String,
    default: ''
  },
  itemTitle: {
    type: String,
    default: ''
  }
})

const router = useRouter()
const loading = ref(false)
const sending = ref(false)
const matchData = ref(null)

const matchScore = computed(() => matchData.value?.match_score || 0)
const isActionable = computed(() => {
  return Boolean(matchData.value?.best_time_label && matchData.value?.best_location)
})
const showProfileTips = computed(() => {
  return Boolean(
    matchData.value?.buyer_missing_time_preferences ||
    matchData.value?.buyer_missing_location_preferences
  )
})

const matchScoreType = computed(() => {
  const score = matchScore.value
  if (score >= 80) return 'success'
  if (score >= 60) return 'warning'
  if (score >= 40) return 'info'
  return 'danger'
})

const recommendationText = computed(() => {
  if (!matchData.value) return ''
  const itemName = props.itemTitle || '这件商品'
  const timeLabel = matchData.value.best_time_label
  const locationLabel = matchData.value.best_location
  if (!timeLabel || !locationLabel) {
    return `你好，我对「${itemName}」感兴趣，想和你协商一个合适的面交时间和地点。`
  }
  return `你好，我对「${itemName}」感兴趣。系统推荐我们优先 ${timeLabel} 在 ${locationLabel} 面交，如果你方便的话我们可以按这个方案沟通一下。`
})

const loadMatchData = async () => {
  loading.value = true
  try {
    const response = await calculateMatch(props.itemId)
    matchData.value = response.data
  } catch (error) {
    console.error('加载匹配数据失败:', error)
    ElMessage.error('加载匹配数据失败')
  } finally {
    loading.value = false
  }
}

const copyRecommendation = async () => {
  try {
    await navigator.clipboard.writeText(recommendationText.value)
    ElMessage.success('推荐方案已复制')
  } catch (error) {
    console.error('复制失败:', error)
    ElMessage.error('复制失败，请手动复制')
  }
}

const openChat = () => {
  if (!props.sellerId) {
    ElMessage.warning('暂时无法定位卖家')
    return
  }
  const username = encodeURIComponent(props.sellerName || '')
  router.push(`/chat/${props.sellerId}?username=${username}`)
}

const goProfile = () => {
  router.push('/profile')
}

const sendRecommendation = async () => {
  if (!props.sellerId) {
    ElMessage.warning('暂时无法定位卖家')
    return
  }
  sending.value = true
  try {
    await chatAPI.sendMessage(props.sellerId, recommendationText.value)
    ElMessage.success('推荐方案已发送给卖家')
  } catch (error) {
    console.error('发送推荐方案失败:', error)
    ElMessage.error(error?.response?.data?.msg || '发送失败，请稍后重试')
  } finally {
    sending.value = false
  }
}

onMounted(() => {
  loadMatchData()
})
</script>

<style scoped>
.time-location-match {
  margin: 20px 0;
}

.match-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.card-subtitle {
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-secondary);
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  gap: 10px;
}

.match-alert {
  margin-bottom: 20px;
}

.profile-tip-box {
  margin-bottom: 20px;
  padding: 16px;
  border-radius: 12px;
  background: color-mix(in srgb, var(--warning-color, #e6a23c) 12%, white 88%);
}

.profile-tip-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.profile-tip-list {
  margin: 0 0 8px;
  padding-left: 18px;
  color: var(--text-secondary);
}

.plan-card {
  margin-bottom: 20px;
  padding: 18px;
  border-radius: 14px;
  border: 1px solid color-mix(in srgb, var(--success-color, #67c23a) 24%, transparent 76%);
  background: linear-gradient(135deg, color-mix(in srgb, var(--success-color, #67c23a) 8%, white 92%), var(--bg-primary));
}

.plan-badge {
  display: inline-flex;
  margin-bottom: 14px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: var(--success-color, #67c23a);
  background: color-mix(in srgb, var(--success-color, #67c23a) 12%, white 88%);
}

.plan-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.plan-item {
  padding: 14px;
  border-radius: 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
}

.plan-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 6px;
}

.plan-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.plan-reason {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.plan-summary {
  margin-top: 14px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text-primary);
}

.plan-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 16px;
}

.match-section {
  margin-bottom: 20px;
}

.match-section h4 {
  margin-bottom: 10px;
  color: var(--text-primary);
  font-size: 14px;
}

.candidate-list {
  display: grid;
  gap: 10px;
}

.candidate-card {
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--border-secondary);
  background: var(--bg-elevated, var(--bg-primary));
}

.candidate-main {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.candidate-label {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.candidate-reason {
  margin-top: 8px;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-secondary);
}

.no-match-tips {
  margin-top: 20px;
}

.no-match-tips p {
  font-weight: 600;
  margin-bottom: 10px;
}

.no-match-tips ul {
  padding-left: 20px;
  color: var(--text-secondary);
}

.no-match-tips li {
  margin-bottom: 8px;
  line-height: 1.6;
}

@media (max-width: 768px) {
  .plan-grid {
    grid-template-columns: 1fr;
  }

  .card-header {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
