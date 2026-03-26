import api from './api'

/**
 * 获取商品评价列表
 */
export const getItemReviews = (itemId) => {
  return api.get(`/reviews/item/${itemId}`)
}

/**
 * 获取用户收到的评价
 */
export const getUserReviews = (userId) => {
  return api.get(`/reviews/user/${userId}`)
}

/**
 * 获取卖家评价
 */
export const getSellerReviews = (sellerId) => {
  return api.get(`/reviews/seller/${sellerId}`)
}

/**
 * 创建评价
 */
export const createReview = (data) => {
  return api.post('/reviews/', data)
}

/**
 * 回复评价
 */
export const replyToReview = (data) => {
  return api.post('/reviews/reply', data)
}

/**
 * 获取订单评价状态
 */
export const getReviewStatus = (orderId) => {
  return api.get(`/reviews/order/${orderId}/status`)
}

/**
 * 获取当前用户对某商品可评价的订单
 */
export const getReviewableOrders = (itemId) => {
  return api.get(`/reviews/item/${itemId}/reviewable-orders`)
}
