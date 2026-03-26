import api from './api'

const normalizeSeller = (seller) => {
  if (!seller) return null
  return {
    ...seller,
    school: seller.school || seller.school_name,
    studentId: seller.studentId || seller.student_id
  }
}

const normalizeProduct = (item) => {
  if (!item) return item
  const seller = normalizeSeller(item.seller)
  const images = item.images || (item.image_url ? [item.image_url] : [])
  return {
    ...item,
    title: item.title || item.name,
    images,
    seller,
    seller_id: item.seller_id || item.user_id,
    seller_name: item.seller_name || seller?.username,
    user_id: item.user_id || item.seller_id || seller?.id,
    location: item.location || item.extra_attributes?.location
  }
}

const normalizeProductList = (items) => {
  return (items || []).map(normalizeProduct)
}

const productAPI = {
  // 获取商品列表
  getProducts: (params) => {
    return api.get('/items', { params }).then(response => {
      response.data.products = normalizeProductList(response.data.products)
      return response
    })
  },
  
  // 获取商品详情
  getProductById: (id) => {
    return api.get(`/items/${id}`).then(response => {
      response.data = normalizeProduct(response.data)
      return response
    })
  },
  
  // 发布商品
  createProduct: (productData) => {
    return api.post('/items/publish', productData)
  },
  
  // 更新商品
  updateProduct: (id, productData) => {
    return api.put(`/items/${id}`, productData)
  },
  
  // 删除商品
  deleteProduct: (id) => {
    return api.delete(`/items/${id}`)
  },
  
  // 下架商品
  offShelf: (id) => {
    return api.put(`/items/${id}/off-shelf`)
  },
  
  // 获取用户的商品
  getUserProducts: (sellerId, status) => {
    const params = {}
    if (sellerId) {
      params.seller_id = sellerId
    }
    if (status && status !== 'all') {
      params.status = status
    }
    return api.get('/items', { params }).then(response => {
      response.data.products = normalizeProductList(response.data.products)
      return response
    })
  },
  
  // 搜索商品
  searchProducts: (keyword, params) => {
    return api.get('/items', { params: { q: keyword, ...params } }).then(response => {
      response.data.products = normalizeProductList(response.data.products)
      return response
    })
  },

  // 获取分类商品
  getCategoryProducts: (categoryId, params) => {
    return api.get('/items', { params: { category_id: categoryId, ...params } }).then(response => {
      response.data.products = normalizeProductList(response.data.products)
      return response
    })
  },

  // 收藏商品
  favoriteProduct: (productId) => {
    return api.post(`/items/${productId}/favorite`)
  },

  // 取消收藏
  unfavoriteProduct: (productId) => {
    return api.delete(`/items/${productId}/favorite`)
  },

  // 获取收藏列表
  getFavorites: () => {
    return api.get('/items/favorites')
  },

  // 记录浏览历史
  recordView: (productId) => {
    return api.post(`/items/${productId}/view`)
  },

  // 获取浏览历史
  getViewHistory: () => {
    return api.get('/items/history')
  },

  // 上传商品图片
  uploadImage: (formData) => {
    return api.post('/items/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
  }
}

export default productAPI
