<template>
  <div class="messages-container">
    <h2 class="page-title">系统消息</h2>
    
    <!-- 消息状态筛选 -->
    <div class="message-filter">
      <el-radio-group v-model="activeStatus" @change="handleStatusChange">
        <el-radio-button value="all">全部</el-radio-button>
        <el-radio-button value="unread">未读</el-radio-button>
        <el-radio-button value="read">已读</el-radio-button>
      </el-radio-group>
      <el-button 
        type="primary" 
        plain 
        size="small"
        @click="handleMarkAllRead"
        :disabled="messages.length === 0"
      >
        全部已读
      </el-button>
    </div>
    
    <!-- 消息列表 -->
    <div class="messages-section">
      <div class="message-list" v-if="messages.length > 0">
        <div 
          v-for="message in messages" 
          :key="message.id"
          class="message-item" 
          :class="{ 'unread': message.status === 'unread' }"
          @click="handleReadMessage(message)"
        >
          <div class="message-badge" v-if="message.status === 'unread'"></div>
          <div class="message-content">
            <div class="message-header">
              <h3 class="message-title">{{ message.title }}</h3>
              <span class="message-time">{{ formatTime(message.created_at) }}</span>
            </div>
            <p class="message-body">{{ message.content }}</p>
            <div class="message-footer">
              <span class="message-type" :class="message.type">{{ getTypeText(message.type) }}</span>
              <span class="message-status">{{ getStatusText(message.status) }}</span>
            </div>
          </div>
        </div>
      </div>
      <div class="empty-state" v-else>
        <el-icon class="empty-icon"><i class="el-icon-bell"></i></el-icon>
        <p class="empty-text">
          {{ activeStatus === 'all' ? '暂无消息' : activeStatus === 'unread' ? '暂无未读消息' : '暂无已读消息' }}
        </p>
      </div>
    </div>
    
    <!-- 分页 -->
    <div class="pagination-section" v-if="total > pageSize">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30]"
        layout="total, sizes, prev, pager, next, jumper"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import chatAPI from '../services/chatAPI'

const activeStatus = ref('all')
const messages = ref([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

const typeText = {
  system: '系统通知',
  trade: '交易通知',
  security: '安全通知',
  activity: '活动通知'
}

const statusText = {
  unread: '未读',
  read: '已读'
}

// 加载消息列表 — 从会话列表聚合
const loadMessages = async () => {
  loading.value = true
  try {
    const response = await chatAPI.getConversations()
    const chats = response.data.chats || []
    // 将会话转换为消息卡片格式
    let list = chats.map(chat => ({
      id: chat.id,
      title: `来自 ${chat.other_user?.username || '未知用户'} 的消息`,
      content: chat.last_message?.content || '暂无消息',
      type: 'trade',
      status: chat.unread_count > 0 ? 'unread' : 'read',
      created_at: chat.last_message?.created_at || '',
      partner_id: chat.id
    }))

    if (activeStatus.value !== 'all') {
      list = list.filter(m => m.status === activeStatus.value)
    }

    messages.value = list
    total.value = list.length
  } catch (error) {
    console.error('获取消息失败:', error)
    messages.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// 处理状态切换
const handleStatusChange = () => {
  currentPage.value = 1
  loadMessages()
}

// 处理阅读消息
const handleReadMessage = async (message) => {
  if (message.status === 'unread') {
    try {
      await chatAPI.markAsRead(message.partner_id)
      message.status = 'read'
    } catch (error) {
      console.error('标记已读失败:', error)
    }
  }
}

// 处理全部已读
const handleMarkAllRead = async () => {
  if (confirm('确定要标记所有消息为已读吗？')) {
    try {
      await chatAPI.markAllMessagesAsRead()
      messages.value.forEach(message => {
        message.status = 'read'
      })
    } catch (error) {
      console.error('标记全部已读失败:', error)
    }
  }
}

// 处理页码变化
const handleCurrentChange = (page) => {
  currentPage.value = page
  loadMessages()
}

// 处理每页条数变化
const handleSizeChange = (size) => {
  pageSize.value = size
  currentPage.value = 1
  loadMessages()
}

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return ''
  return new Date(timeString).toLocaleString('zh-CN')
}

// 获取消息类型文本
const getTypeText = (type) => {
  return typeText[type] || '其他'
}

// 获取消息状态文本
const getStatusText = (status) => {
  return statusText[status] || '未知'
}

onMounted(() => {
  loadMessages()
})
</script>

<style scoped>
.messages-container {
  padding: 20px 0;
}

.page-title {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 30px;
  color: var(--text-primary);
}

/* 消息筛选 */
.message-filter {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 30px;
}

/* 消息列表 */
.messages-section {
  margin-bottom: 30px;
}

.message-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.message-item {
  display: flex;
  align-items: flex-start;
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px var(--black-alpha-10);
  transition: all 0.3s;
  cursor: pointer;
}

.message-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px var(--black-alpha-20);
}

.message-item.unread {
  border-left: 4px solid var(--primary-color);
}

.message-badge {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--danger-color);
  margin-right: 15px;
  margin-top: 8px;
}

.message-content {
  flex: 1;
}

.message-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 10px;
}

.message-title {
  font-size: 16px;
  font-weight: bold;
  margin: 0;
  color: var(--text-primary);
}

.message-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.message-body {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 15px;
}

.message-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.message-type {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.message-type.system {
  background: color-mix(in srgb, var(--primary-color) 16%, transparent 84%);
  color: var(--primary-color);
}

.message-type.trade {
  background: color-mix(in srgb, var(--success-color) 16%, transparent 84%);
  color: var(--success-color);
}

.message-type.security {
  background: color-mix(in srgb, var(--danger-color) 16%, transparent 84%);
  color: var(--danger-color);
}

.message-type.activity {
  background: color-mix(in srgb, var(--warning-color) 16%, transparent 84%);
  color: var(--warning-color);
}

.message-status {
  font-size: 12px;
  color: var(--text-tertiary);
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px var(--black-alpha-10);
}

.empty-icon {
  font-size: 64px;
  color: var(--text-quaternary);
  margin-bottom: 20px;
}

.empty-text {
  font-size: 16px;
  color: var(--text-tertiary);
}

/* 分页 */
.pagination-section {
  display: flex;
  justify-content: center;
  margin-top: 30px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .message-filter {
    flex-direction: column;
    align-items: flex-start;
    gap: 15px;
  }
  
  .message-item {
    padding: 15px;
  }
  
  .message-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 5px;
  }
  
  .message-time {
    margin-top: 4px;
  }
  
  .message-footer {
    flex-direction: column;
    align-items: flex-start;
    gap: 10px;
  }
}

@media (max-width: 480px) {
  .message-item {
    padding: 12px;
  }
  
  .message-title {
    font-size: 14px;
  }
  
  .message-body {
    font-size: 13px;
  }
}
</style>
