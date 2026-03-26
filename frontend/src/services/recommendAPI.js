import api from './api'

const recommendAPI = {
  // 获取个性化推荐（首页"猜你喜欢"）
  getPersonalRecommendations: (limit = 20, options = {}) => {
    const params = { limit }
    if (options.forceRefresh) {
      params.force_refresh = 1
    }
    return api.get('/recommendations/personal', { params }).then(response => {
      // 复用 productAPI 的字段标准化
      const products = (response.data.products || []).map(item => ({
        ...item,
        title: item.title || item.name,
        images: item.images || [],
        seller_name: item.seller?.username,
        user_id: item.seller_id || item.seller?.id
      }))
      response.data.products = products
      return response
    })
  },

  // 获取相似商品推荐（商品详情页）
  getSimilarItems: (itemId, limit = 10) => {
    return api.get(`/recommendations/similar/${itemId}`, { params: { limit } }).then(response => {
      const products = (response.data.products || []).map(item => ({
        ...item,
        title: item.title || item.name,
        images: item.images || [],
        seller_name: item.seller?.username,
        user_id: item.seller_id || item.seller?.id
      }))
      response.data.products = products
      return response
    })
  },

  // 获取定价建议
  getPriceSuggestion: (itemId) => {
    return api.get(`/recommendations/price-suggestion/${itemId}`)
  }
}

export default recommendAPI
