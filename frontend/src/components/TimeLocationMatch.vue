<template>
  <div class="time-location-match">
    <el-card class="match-card">
      <template #header>
        <div class="card-header">
          <span>时空匹配度</span>
          <el-tag :type="matchScoreType" size="large">
            {{ matchScore }}分
          </el-tag>
        </div>
      </template>

      <div v-if="loading" class="loading-container">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>计算匹配度中...</span>
      </div>

      <div v-else-if="matchData">
        <el-alert
          :title="matchData.message"
          :type="matchData.has_match ? 'success' : 'warning'"
          :closable="false"
          show-icon
          class="match-alert"
        />

        <div v-if="matchData.common_time_slots && matchData.common_time_slots.length > 0" class="match-section">
          <h4>共同可交易时间</h4>
          <el-space wrap>
            <el-tag
              v-for="(slot, index) in matchData.common_time_slots"
              :key="index"
              type="success"
              effect="plain"
            >
              {{ slot }}
            </el-tag>
          </el-space>
        </div>

        <div v-if="matchData.common_locations && matchData.common_locations.length > 0" class="match-section">
          <h4>共同交易地点</h4>
          <el-space wrap>
            <el-tag
              v-for="(location, index) in matchData.common_locations"
              :key="index"
              type="success"
              effect="plain"
            >
              {{ location }}
            </el-tag>
          </el-space>
        </div>

        <div v-if="!matchData.has_match" class="no-match-tips">
          <el-divider />
          <p>建议：</p>
          <ul>
            <li>可以通过站内消息与卖家协商具体的交易时间和地点</li>
            <li>选择公共区域进行面交，确保交易安全</li>
            <li>保留平台内的沟通记录</li>
          </ul>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { calculateMatch } from '@/services/timeLocationAPI'
import { Loading } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps({
  itemId: {
    type: Number,
    required: true
  }
})

const loading = ref(false)
const matchData = ref(null)

const matchScore = computed(() => {
  return matchData.value?.match_score || 0
})

const matchScoreType = computed(() => {
  const score = matchScore.value
  if (score >= 80) return 'success'
  if (score >= 50) return 'warning'
  return 'danger'
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

.match-section {
  margin-bottom: 20px;
}

.match-section h4 {
  margin-bottom: 10px;
  color: var(--text-primary);
  font-size: 14px;
}

.no-match-tips {
  margin-top: 20px;
}

.no-match-tips p {
  font-weight: bold;
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
</style>
