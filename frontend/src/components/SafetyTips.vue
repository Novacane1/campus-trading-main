<template>
  <div class="safety-tips-container">
    <el-alert
      v-for="(tip, index) in tips"
      :key="index"
      :title="tip.title"
      :type="tip.type"
      :description="tip.content"
      :closable="true"
      show-icon
      class="tip-item"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSafetyTips } from '@/services/riskAPI'
import { ElMessage } from 'element-plus'

const tips = ref([])

const loadSafetyTips = async () => {
  try {
    const response = await getSafetyTips()
    tips.value = response.data || []
  } catch (error) {
    console.error('加载安全提示失败:', error)
  }
}

onMounted(() => {
  loadSafetyTips()
})
</script>

<style scoped>
.safety-tips-container {
  margin: 20px 0;
}

.tip-item {
  margin-bottom: 12px;
}
</style>
