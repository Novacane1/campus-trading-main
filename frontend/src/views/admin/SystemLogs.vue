<template>
  <div class="system-logs">
    <el-card>
      <template #header>
        <div class="card-header">
          <div class="header-left">
            <el-radio-group v-model="logLevel" size="small" @change="handleFilter">
              <el-radio-button value="all">全部</el-radio-button>
              <el-radio-button value="info">信息</el-radio-button>
              <el-radio-button value="warn">警告</el-radio-button>
              <el-radio-button value="error">错误</el-radio-button>
            </el-radio-group>
          </div>
          <div class="header-right">
            <el-button size="small" @click="clearLogs">清空当前显示</el-button>
            <el-button size="small" type="primary" @click="exportLogs">导出日志</el-button>
          </div>
        </div>
      </template>

      <div class="log-panel" ref="logPanelRef">
        <div v-for="(log, index) in filteredLogs" :key="index" class="log-line" :class="log.level">
          <span class="log-time">[{{ log.time }}]</span>
          <span class="log-level">[{{ log.level.toUpperCase() }}]</span>
          <span class="log-user" v-if="log.user">[{{ log.user }}]</span>
          <span class="log-message">{{ log.message }}</span>
          <span class="log-ip" v-if="log.ip"> (IP: {{ log.ip }})</span>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import adminAPI from '../../services/adminAPI'

const logLevel = ref('all')
const logPanelRef = ref(null)
const loading = ref(false)

const logs = ref([])

const fetchLogs = async () => {
  loading.value = true
  try {
    const res = await adminAPI.getLogs({
      page: 1,
      per_page: 200,
      level: logLevel.value !== 'all' ? logLevel.value : undefined
    })
    logs.value = (res.data.logs || []).map(log => ({
      time: log.created_at,
      level: log.level || 'info',
      user: log.username || 'system',
      message: log.detail || log.action || '',
      ip: log.ip_address || ''
    }))
    scrollToBottom()
  } catch (e) {
    ElMessage.error('获取日志失败')
  } finally {
    loading.value = false
  }
}

const filteredLogs = computed(() => {
  if (logLevel.value === 'all') return logs.value
  return logs.value.filter(log => log.level === logLevel.value)
})

const handleFilter = () => {
  fetchLogs()
}

const scrollToBottom = () => {
  nextTick(() => {
    if (logPanelRef.value) {
      logPanelRef.value.scrollTop = logPanelRef.value.scrollHeight
    }
  })
}

const clearLogs = () => {
  logs.value = []
  ElMessage.success('已清空显示内容')
}

const exportLogs = () => {
  const text = logs.value.map(l => `[${l.time}] [${l.level.toUpperCase()}] [${l.user}] ${l.message} ${l.ip ? '(IP: ' + l.ip + ')' : ''}`).join('\n')
  const blob = new Blob([text], { type: 'text/plain' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `system-logs-${new Date().toISOString().slice(0, 10)}.txt`
  a.click()
  URL.revokeObjectURL(url)
  ElMessage.success('日志导出成功')
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.log-panel {
  height: 600px;
  background-color: var(--bg-primary);
  color: var(--text-secondary);
  padding: 16px;
  font-family: 'Courier New', Courier, monospace;
  font-size: 13px;
  overflow-y: auto;
  border-radius: 4px;
  line-height: 1.6;
}

.log-line {
  margin-bottom: 4px;
  white-space: pre-wrap;
  word-break: break-all;
}

.log-time {
  color: var(--success-color);
  margin-right: 8px;
}

.log-level {
  margin-right: 8px;
  font-weight: bold;
}

.info .log-level { color: var(--primary-color); }
.warn .log-level { color: var(--warning-color); }
.error .log-level { color: var(--danger-color); }

.log-user {
  color: var(--primary-hover);
  margin-right: 8px;
}

.log-ip {
  color: var(--text-tertiary);
  font-style: italic;
}

.log-panel::-webkit-scrollbar {
  width: 8px;
}

.log-panel::-webkit-scrollbar-thumb {
  background-color: var(--text-primary);
  border-radius: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
