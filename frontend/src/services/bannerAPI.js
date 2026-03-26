import api from './api'

const bannerAPI = {
  // 获取已发布的Banner列表
  getBanners: () => {
    return api.get('/banners/')
  }
}

export default bannerAPI
