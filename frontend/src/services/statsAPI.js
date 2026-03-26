import api from './api'

const statsAPI = {
  getOverview: () => {
    return api.get('/stats/overview')
  },

  getPriceTrends: () => {
    return api.get('/stats/price-trends')
  },

  getCategoryDistribution: () => {
    return api.get('/stats/category-distribution')
  },

  getSupplyDemand: () => {
    return api.get('/stats/supply-demand')
  },

  getCategoryPriceTrends: (categoryId, days = 30) => {
    return api.get('/stats/category-price-trends', {
      params: { category_id: categoryId, days }
    })
  },

  getPriceDistribution: (categoryId = null) => {
    return api.get('/stats/price-distribution', {
      params: categoryId ? { category_id: categoryId } : {}
    })
  },

  getSupplyDemandRatio: () => {
    return api.get('/stats/supply-demand-ratio')
  },

  getCategoryAvgPrice: () => {
    return api.get('/stats/category-avg-price')
  },

  getCategoryAvgPrices: () => {
    return api.get('/stats/category-avg-price')
  }
}

export default statsAPI
