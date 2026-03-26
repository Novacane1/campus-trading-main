import api from './api'

const chatAPI = {
  // 获取聊天列表
  getConversations: () => {
    return api.get('/chat/conversations')
  },
  
  // 获取聊天记录
  getMessages: (userId, params) => {
    return api.get(`/chat/messages/${userId}`, { params })
  },
  
  // 发送消息
  sendMessage: (userId, content, type = 'text') => {
    return api.post(`/chat/messages/${userId}`, { content, type })
  },
  
  // 标记消息已读
  markAsRead: (userId) => {
    return api.put(`/chat/messages/${userId}/read`)
  },
  
  // 获取未读消息数
  getUnreadCount: () => {
    return api.get('/chat/unread-count')
  },
  
  // 删除聊天记录
  deleteConversation: (userId) => {
    return api.delete(`/chat/conversations/${userId}`)
  },

  // 兼容别名 - Chat.vue 使用 getChats
  getChats: () => {
    return api.get('/chat/conversations')
  },

  // 标记单条消息已读
  markMessageAsRead: (messageId) => {
    return api.put(`/chat/messages/${messageId}/mark-read`)
  },

  // 标记所有消息已读
  markAllMessagesAsRead: () => {
    return api.put('/chat/messages/read-all')
  }
}

export default chatAPI
