import api from './api'

const categoryAPI = {
  // 获取分类列表（树形结构）
  getCategories: () => {
    return api.get('/categories/all')
  },
  
  // 获取分类详情
  getCategoryById: (id) => {
    return api.get(`/categories/${id}`)
  },
  
  // 创建分类（用户申请）
  applyCategory: (categoryData) => {
    return api.post('/applications/', {
      type: 'category',
      name: categoryData.name,
      description: categoryData.description || ''
    })
  },

  // 获取我的申请列表
  getCategoryApplications: () => {
    return api.get('/applications/me')
  },
  
  // 更新分类
  updateCategory: (id, categoryData) => {
    return api.put(`/categories/${id}`, categoryData)
  },
  
  // 删除分类
  deleteCategory: (id) => {
    return api.delete(`/categories/${id}`)
  }
}

export default categoryAPI
