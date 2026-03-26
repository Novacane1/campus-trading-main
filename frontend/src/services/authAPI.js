import api from './api'

const authAPI = {
  // 登录
  login: (credentials) => {
    return api.post('/auth/login', credentials)
  },
  
  // 注册
  register: (userData) => {
    return api.post('/auth/register', userData)
  },
  
  // 登出
  logout: () => {
    return api.post('/auth/logout')
  },
  
  // 找回密码
  forgotPassword: (email) => {
    return api.post('/auth/forgot-password', { email })
  },
  
  // 重置密码
  resetPassword: (token, newPassword) => {
    return api.post('/auth/reset-password', { token, newPassword })
  },
  
  // 修改密码
  changePassword: (passwordData) => {
    return api.post('/auth/change-password', passwordData)
  },
  
  // 获取用户信息
  getUserInfo: () => {
    return api.get('/auth/me')
  },

  getUserById: (userId) => {
    return api.get(`/auth/user/${userId}`)
  },
  
  // 验证邮箱
  verifyEmail: (token) => {
    return api.get(`/auth/verify-email/${token}`)
  },
  
  // 重发验证邮件
  resendVerificationEmail: (email) => {
    return api.post('/auth/resend-verification', { email })
  },

  // 更新个人资料
  updateProfile: (profileData) => {
    return api.put('/auth/profile', profileData)
  },

  // 学生身份验证（模拟学信网）
  verifyStudent: (data) => {
    return api.post('/verification/verify-student', data)
  },

  // 获取学校列表
  getSchools: () => {
    return api.get('/verification/schools')
  }
}

export default authAPI
