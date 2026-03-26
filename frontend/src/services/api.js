import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    // 从本地存储获取token
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response
  },
  error => {
    // 处理错误
    if (error.response) {
      console.error('API Error Status:', error.response.status, 'URL:', error.config.url);
      // 服务器返回错误
      switch (error.response.status) {
        case 401:
          // 未授权，清除token并跳转到登录页
          // 只有当不在登录页时才跳转，避免循环重定向
          if (!window.location.pathname.includes('/login')) {
            console.warn('Unauthorized access, redirecting to login...');
            localStorage.removeItem('token')
            localStorage.removeItem('userInfo')
            // 使用 import 动态加载避免循环依赖
            import('element-plus').then(({ ElMessage }) => {
              ElMessage.warning('登录已过期，请重新登录')
            })
            setTimeout(() => {
              window.location.href = '/login'
            }, 500)
          }
          break
        case 403:
          // 禁止访问
          console.error('没有权限访问该资源')
          break
        case 404:
          // 资源不存在
          console.error('请求的资源不存在')
          break
        case 500:
          // 服务器错误
          console.error('服务器内部错误')
          break
        default:
          console.error('请求失败:', error.response.data.message || '未知错误')
      }
    } else if (error.request) {
      // 请求已发送但没有收到响应
      console.error('网络错误，请检查您的网络连接')
    } else {
      // 请求配置错误
      console.error('请求配置错误:', error.message)
    }
    return Promise.reject(error)
  }
)

export default api
