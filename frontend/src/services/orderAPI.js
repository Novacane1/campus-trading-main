import api from './api'

const orderAPI = {
  createOrder: (data) => {
    return api.post('/orders', data)
  },

  batchCreateOrder: (itemIds) => {
    return api.post('/orders/batch', { item_ids: itemIds })
  },

  getMyOrders: (params) => {
    return api.get('/orders/me', { params })
  },

  getMySales: (params) => {
    return api.get('/orders/sales', { params })
  },

  getOrderDetail: (orderId) => {
    return api.get(`/orders/${orderId}`)
  },

  updateOrderStatus: (orderId, status) => {
    return api.put(`/orders/${orderId}/status`, { status })
  },

  confirmOrder: (orderId) => {
    return api.put(`/orders/${orderId}/confirm`)
  }
}

export default orderAPI
