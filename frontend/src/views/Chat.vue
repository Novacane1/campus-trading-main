<template>
  <div class="chat-container">
    <div class="chat-sidebar">
      <div class="chat-sidebar-header">
        <h3 class="sidebar-title">消息列表</h3>
      </div>
      <div class="chat-list">
        <div 
          v-for="chat in chats" 
          :key="chat.id"
          class="chat-item" 
          :class="{ active: selectedChatId === chat.id }"
          @click="selectChat(chat)"
        >
          <div class="chat-avatar">
            {{ chat.other_user?.username?.charAt(0)?.toUpperCase() || '?' }}
          </div>
          <div class="chat-info">
            <div class="chat-user-info">
              <span class="chat-username">{{ chat.other_user?.username || '未知用户' }}</span>
              <span class="chat-time">{{ formatTime(chat.last_message?.created_at) }}</span>
            </div>
            <div class="chat-last-message" v-if="chat.last_message">
              <span class="message-sender" v-if="chat.last_message.sender_id !== userInfo.id">
                {{ chat.other_user?.username || '对方' }}:
              </span>
              <span class="message-content">{{ chat.last_message.content }}</span>
            </div>
            <div class="chat-last-message" v-else>
              <span class="message-content">开始聊天吧</span>
            </div>
          </div>
          <div class="chat-badge" v-if="chat.unread_count > 0">
            {{ chat.unread_count }}
          </div>
        </div>
      </div>
    </div>
    
    <div class="chat-main" v-if="selectedChat">
      <div class="chat-header">
        <div class="chat-header-info">
          <h3 class="chat-title">{{ selectedChat.other_user?.username || '未知用户' }}</h3>
          <span class="chat-status">在线</span>
        </div>
        <div class="chat-header-actions">
          <el-button type="text" @click="showUserInfo(selectedChat.other_user)">
            <el-icon><i class="el-icon-user"></i></el-icon>
            查看资料
          </el-button>
        </div>
      </div>
      
      <div class="chat-body" ref="chatBody">
        <div
          v-for="message in selectedChat.messages"
          :key="message.id"
          class="message-item"
          :class="{ 'message-sent': message.sender_id === userInfo.id }"
        >
          <div class="message-content">
            <div class="message-bubble">
              {{ message.content }}
            </div>
            <div class="message-meta">
              <span class="message-time">{{ formatTime(message.created_at) }}</span>
              <span v-if="message.sender_id === userInfo.id" class="message-read-status" :class="{ 'is-read': message.is_read }">
                {{ message.is_read ? '已读' : '未读' }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <div class="chat-footer">
        <el-input
          v-model="messageInput"
          type="textarea"
          :rows="1"
          placeholder="输入消息..."
          resize="none"
          @keyup.enter.ctrl="sendMessage"
          class="message-input"
        />
        <div class="chat-footer-actions">
          <el-button type="primary" @click="sendMessage">
            发送
          </el-button>
        </div>
      </div>
    </div>
    
    <div class="chat-empty" v-else>
      <el-icon class="empty-icon"><i class="el-icon-chat-dot-round"></i></el-icon>
      <p class="empty-text">选择一个聊天开始对话</p>
      <p class="empty-hint">您可以在商品详情页联系卖家</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../stores/user'
import chatAPI from '../services/chatAPI'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const chats = ref([])
const selectedChatId = ref(null)
const selectedChat = ref(null)
const messageInput = ref('')
const chatBody = ref(null)
let pollTimer = null
let msgPollTimer = null

const userInfo = computed(() => userStore.userInfo)

// 加载聊天列表
const loadChats = async () => {
  try {
    const response = await chatAPI.getChats()
    const newChats = response.data.chats || []
    // 保留已加载的 messages
    for (const nc of newChats) {
      const existing = chats.value.find(c => c.id === nc.id)
      nc.messages = existing ? existing.messages : []
    }
    chats.value = newChats
    // 如果当前选中的聊天还在列表中，更新引用
    if (selectedChatId.value) {
      selectedChat.value = chats.value.find(c => c.id === selectedChatId.value) || null
    }
  } catch (error) {
    console.error('获取聊天列表失败:', error)
  }
}

// 加载聊天消息
const loadMessages = async (chatId) => {
  try {
    const response = await chatAPI.getMessages(chatId)
    const chat = chats.value.find(c => c.id === chatId)
    if (chat) {
      chat.messages = response.data.messages || []
    }
  } catch (error) {
    console.error('获取消息失败:', error)
  }
}

// 轮询当前对话的新消息
const pollMessages = async () => {
  if (!selectedChatId.value) return
  const oldLen = selectedChat.value?.messages?.length || 0
  await loadMessages(selectedChatId.value)
  const newLen = selectedChat.value?.messages?.length || 0
  if (newLen > oldLen) {
    scrollToBottom()
    markAsRead(selectedChatId.value)
  }
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatBody.value) {
      chatBody.value.scrollTop = chatBody.value.scrollHeight
    }
  })
}

// 选择聊天
const selectChat = async (chat) => {
  selectedChatId.value = chat.id
  selectedChat.value = chat
  await loadMessages(chat.id)
  scrollToBottom()
  markAsRead(chat.id)
  // 开始轮询当前对话
  startMsgPolling()
}

// 标记已读
const markAsRead = async (chatId) => {
  try {
    await chatAPI.markAsRead(chatId)
    const chat = chats.value.find(c => c.id === chatId)
    if (chat) {
      chat.unread_count = 0
    }
  } catch (error) {
    console.error('标记已读失败:', error)
  }
}

// 发送消息
const sendMessage = async () => {
  if (!messageInput.value.trim() || !selectedChatId.value) return
  const content = messageInput.value.trim()
  messageInput.value = ''
  const newMessage = {
    id: Date.now(),
    content,
    sender_id: userInfo.value.id,
    is_read: false,
    created_at: new Date().toISOString()
  }
  selectedChat.value.messages.push(newMessage)
  scrollToBottom()
  try {
    const res = await chatAPI.sendMessage(selectedChatId.value, content)
    // 用服务器返回的真实消息替换临时消息
    const idx = selectedChat.value.messages.indexOf(newMessage)
    if (idx !== -1 && res.data) {
      selectedChat.value.messages.splice(idx, 1, res.data)
    }
    const chat = chats.value.find(c => c.id === selectedChatId.value)
    if (chat) {
      chat.last_message = { id: res.data?.id || newMessage.id, content, sender_id: userInfo.value.id, created_at: newMessage.created_at }
    }
  } catch (error) {
    console.error('发送消息失败:', error)
    selectedChat.value.messages.pop()
  }
}

// 如果从商品详情页带了 userId 参数，自动打开对话
const initFromRoute = async () => {
  const partnerId = Number(route.params.userId)
  if (!partnerId) return
  let chat = chats.value.find(c => c.id === partnerId)
  if (!chat) {
    // 对方不在列表中，尝试获取消息记录
    let messages = []
    let partnerName = route.query.username || '用户'
    try {
      const res = await chatAPI.getMessages(partnerId)
      messages = res.data.messages || []
      // 从消息中的 sender 信息获取用户名
      const partnerMsg = messages.find(m => m.sender_id === partnerId)
      if (partnerMsg?.sender?.username) {
        partnerName = partnerMsg.sender.username
      }
    } catch {
      // ignore
    }
    chat = {
      id: partnerId,
      other_user: { id: partnerId, username: partnerName },
      last_message: messages.length > 0 ? messages[messages.length - 1] : null,
      unread_count: 0,
      messages
    }
    chats.value.unshift(chat)
  }
  selectChat(chat)
}

// 查看用户资料
const showUserInfo = (user) => {
  if (user?.id) {
    router.push(`/user/${user.id}`)
  }
}

// 格式化时间
const formatTime = (timeString) => {
  if (!timeString) return ''
  const date = new Date(timeString)
  const now = new Date()
  const diff = now - date
  if (diff < 60 * 1000) return '刚刚'
  if (diff < 60 * 60 * 1000) return `${Math.floor(diff / (60 * 1000))}分钟前`
  if (diff < 24 * 60 * 60 * 1000) return `${Math.floor(diff / (60 * 60 * 1000))}小时前`
  if (diff < 7 * 24 * 60 * 60 * 1000) return `${Math.floor(diff / (24 * 60 * 60 * 1000))}天前`
  return date.toLocaleDateString('zh-CN')
}

const startMsgPolling = () => {
  if (msgPollTimer) clearInterval(msgPollTimer)
  msgPollTimer = setInterval(pollMessages, 3000)
}

onMounted(async () => {
  await loadChats()
  initFromRoute()
  // 轮询聊天列表（更新未读数等）
  pollTimer = setInterval(loadChats, 5000)
})

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
  if (msgPollTimer) clearInterval(msgPollTimer)
})
</script>

<style scoped>
.chat-container {
  display: flex;
  height: calc(100vh - 120px);
  background: var(--bg-secondary);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px var(--black-alpha-10);
}

/* 侧边栏 */
.chat-sidebar {
  width: 300px;
  background: var(--bg-primary);
  border-right: 1px solid var(--border-secondary);
  display: flex;
  flex-direction: column;
}

.chat-sidebar-header {
  padding: 20px;
  border-bottom: 1px solid var(--border-secondary);
}

.sidebar-title {
  font-size: 16px;
  font-weight: bold;
  margin: 0;
  color: var(--text-primary);
}

.chat-list {
  flex: 1;
  overflow-y: auto;
}

.chat-item {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  cursor: pointer;
  transition: all 0.3s;
  border-bottom: 1px solid var(--border-secondary);
}

.chat-item:hover {
  background: var(--bg-secondary);
}

.chat-item.active {
  background: color-mix(in srgb, var(--primary-color) 16%, transparent 84%);
}

.chat-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-color);
  color: var(--bg-primary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  font-weight: bold;
  margin-right: 12px;
}

.chat-info {
  flex: 1;
  min-width: 0;
}

.chat-user-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.chat-username {
  font-size: 14px;
  font-weight: bold;
  color: var(--text-primary);
}

.chat-time {
  font-size: 12px;
  color: var(--text-tertiary);
}

.chat-last-message {
  font-size: 12px;
  color: var(--text-secondary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.message-sender {
  color: var(--text-tertiary);
}

.chat-badge {
  background: var(--danger-color);
  color: var(--bg-primary);
  font-size: 12px;
  font-weight: bold;
  min-width: 20px;
  height: 20px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 6px;
}

/* 主聊天区域 */
.chat-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px 20px;
  border-bottom: 1px solid var(--border-secondary);
  background: var(--bg-secondary);
}

.chat-title {
  font-size: 16px;
  font-weight: bold;
  margin: 0;
  color: var(--text-primary);
}

.chat-status {
  font-size: 12px;
  color: var(--success-color);
  margin-left: 8px;
}

.chat-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
  background: var(--bg-secondary);
}

.message-item {
  display: flex;
  margin-bottom: 15px;
  align-items: flex-end;
}

.message-item.message-sent {
  justify-content: flex-end;
}

.message-content {
  max-width: 70%;
}

.message-bubble {
  padding: 10px 14px;
  border-radius: 8px;
  font-size: 14px;
  line-height: 1.4;
  word-wrap: break-word;
}

.message-item:not(.message-sent) .message-bubble {
  background: var(--bg-primary);
  border: 1px solid var(--border-secondary);
  border-bottom-left-radius: 2px;
  color: var(--text-primary);
}

.message-item.message-sent .message-bubble {
  background: var(--primary-color);
  color: var(--bg-primary);
  border-bottom-right-radius: 2px;
}

.message-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 4px;
}

.message-meta .message-time {
  font-size: 11px;
  color: var(--text-tertiary);
}

.message-item.message-sent .message-meta {
  justify-content: flex-end;
}

.message-read-status {
  font-size: 11px;
  color: var(--text-tertiary);
}

.message-read-status.is-read {
  color: var(--primary-color);
}

.message-item:not(.message-sent) .message-meta {
  justify-content: flex-start;
}

.chat-footer {
  padding: 15px 20px;
  border-top: 1px solid var(--border-secondary);
  background: var(--bg-primary);
}

.message-input {
  margin-bottom: 10px;
  border-radius: 4px;
}

.chat-footer-actions {
  display: flex;
  justify-content: flex-end;
}

/* 空状态 */
.chat-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
}

.empty-icon {
  font-size: 64px;
  color: var(--text-quaternary);
  margin-bottom: 20px;
}

.empty-text {
  font-size: 16px;
  color: var(--text-primary);
  margin-bottom: 10px;
  font-weight: bold;
}

.empty-hint {
  font-size: 14px;
  color: var(--text-tertiary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-container {
    height: calc(100vh - 100px);
  }
  
  .chat-sidebar {
    width: 250px;
  }
  
  .message-content {
    max-width: 80%;
  }
}

@media (max-width: 480px) {
  .chat-container {
    height: calc(100vh - 80px);
  }
  
  .chat-sidebar {
    width: 200px;
  }
  
  .chat-item {
    padding: 10px 15px;
  }
  
  .chat-avatar {
    width: 32px;
    height: 32px;
    font-size: 12px;
  }
  
  .chat-body {
    padding: 15px;
  }
  
  .message-bubble {
    padding: 8px 12px;
    font-size: 13px;
  }
}
</style>
