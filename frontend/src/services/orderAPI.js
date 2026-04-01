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

  createAlipayPagePayment: (orderId) => {
    return api.post('/payments/alipay/page', { order_id: orderId })
  },

  syncAlipayOrderStatus: (orderId) => {
    return api.get(`/payments/alipay/orders/${orderId}/status`)
  },

  updateOrderStatus: (orderId, status) => {
    return api.put(`/orders/${orderId}/status`, { status })
  },

  confirmOrder: (orderId) => {
    return api.put(`/orders/${orderId}/confirm`)
  }
}

export default orderAPI
