import api from './api'

const announcementAPI = {
  // 获取已发布的公告列表
  getAnnouncements: (params) => {
    return api.get('/announcements/', { params })
  },

  // 获取最新公告（首页展示）
  getLatestAnnouncements: (limit = 5) => {
    return api.get('/announcements/latest', { params: { limit } })
  },

  // 获取公告详情
  getAnnouncementDetail: (id) => {
    return api.get(`/announcements/${id}`)
  }
}

export default announcementAPI
