import api from './api'

const adminAPI = {
  getDashboard: () => {
    return api.get('/admin/dashboard')
  },

  getUsers: (params) => {
    return api.get('/admin/users', { params })
  },

  updateUser: (userId, data) => {
    return api.put(`/admin/users/${userId}`, data)
  },

  deleteUser: (userId) => {
    return api.delete(`/admin/users/${userId}`)
  },

  getProducts: (params) => {
    return api.get('/admin/products', { params })
  },

  approveProduct: (productId) => {
    return api.put(`/admin/products/${productId}/approve`)
  },

  rejectProduct: (productId, reason) => {
    return api.put(`/admin/products/${productId}/reject`, { reason })
  },

  deleteProduct: (productId) => {
    return api.delete(`/admin/products/${productId}`)
  },

  getLogs: (params) => {
    return api.get('/admin/logs', { params })
  },

  exportLogs: (params) => {
    return api.get('/admin/logs/export', {
      params,
      responseType: 'blob'
    })
  },

  createCategory: (data) => {
    return api.post('/admin/categories', data)
  },

  updateCategory: (catId, data) => {
    return api.put(`/admin/categories/${catId}`, data)
  },

  deleteCategory: (catId) => {
    return api.delete(`/admin/categories/${catId}`)
  },

  getApplications: (params) => {
    return api.get('/admin/applications', { params })
  },

  approveApplication: (appId) => {
    return api.put(`/admin/applications/${appId}/approve`)
  },

  rejectApplication: (appId, reason) => {
    return api.put(`/admin/applications/${appId}/reject`, { reason })
  },

  togglePublish: (userId, canPublish) => {
    return api.put(`/admin/users/${userId}/toggle-publish`, { can_publish: canPublish })
  },

  // 订单管理
  getOrders: (params) => {
    return api.get('/admin/orders', { params })
  },

  getOrderDetail: (orderId) => {
    return api.get(`/admin/orders/${orderId}`)
  },

  updateOrderStatus: (orderId, data) => {
    return api.put(`/admin/orders/${orderId}/status`, data)
  },

  extendOrderTime: (orderId, data) => {
    return api.put(`/admin/orders/${orderId}/extend`, data)
  },

  refundOrder: (orderId, data) => {
    return api.put(`/admin/orders/${orderId}/refund`, data)
  },

  // 评价管理
  getReviews: (params) => {
    return api.get('/admin/reviews', { params })
  },

  deleteReview: (reviewId, data) => {
    return api.delete(`/admin/reviews/${reviewId}`, { data })
  },

  // 公告管理
  getAnnouncements: (params) => {
    return api.get('/admin/announcements', { params })
  },

  createAnnouncement: (data) => {
    return api.post('/admin/announcements', data)
  },

  updateAnnouncement: (annId, data) => {
    return api.put(`/admin/announcements/${annId}`, data)
  },

  deleteAnnouncement: (annId) => {
    return api.delete(`/admin/announcements/${annId}`)
  },

  publishAnnouncement: (annId) => {
    return api.put(`/admin/announcements/${annId}/publish`)
  },

  // 举报管理
  getReports: (params) => {
    return api.get('/admin/reports', { params })
  },

  handleReport: (reportId, data) => {
    return api.put(`/admin/reports/${reportId}/handle`, data)
  },

  // 申诉管理
  getAppeals: (params) => {
    return api.get('/admin/appeals', { params })
  },

  handleAppeal: (appealId, data) => {
    return api.put(`/admin/appeals/${appealId}/handle`, data)
  },

  // Banner管理
  getBanners: () => {
    return api.get('/admin/banners')
  },

  createBanner: (data) => {
    return api.post('/admin/banners', data)
  },

  updateBanner: (bannerId, data) => {
    return api.put(`/admin/banners/${bannerId}`, data)
  },

  deleteBanner: (bannerId) => {
    return api.delete(`/admin/banners/${bannerId}`)
  },

  sortBanners: (bannerIds) => {
    return api.put('/admin/banners/sort', { banner_ids: bannerIds })
  }
}

export default adminAPI
