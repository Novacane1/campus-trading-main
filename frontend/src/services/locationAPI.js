import api from './api'

const locationAPI = {
  // 获取交易地点列表
  getLocations: () => {
    return api.get('/locations')
  },
  
  // 获取地点详情
  getLocationById: (id) => {
    return api.get(`/locations/${id}`)
  },
  
  // 创建交易地点
  createLocation: (locationData) => {
    return api.post('/locations', locationData)
  },
  
  // 更新交易地点
  updateLocation: (id, locationData) => {
    return api.put(`/locations/${id}`, locationData)
  },
  
  // 删除交易地点
  deleteLocation: (id) => {
    return api.delete(`/locations/${id}`)
  },
  
  // 获取用户常用地点
  getUserLocations: () => {
    return api.get('/locations/user')
  },
  
  // 添加常用地点
  addUserLocation: (locationData) => {
    return api.post('/locations/user', locationData)
  },
  
  // 删除常用地点
  removeUserLocation: (id) => {
    return api.delete(`/locations/user/${id}`)
  },

  // 申请新交易地点
  applyLocation: (locationData) => {
    return api.post('/applications', {
      type: 'location',
      name: locationData.name,
      description: locationData.description,
      extra_type: locationData.type
    })
  }
}

export default locationAPI
