import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import authAPI from '../services/authAPI'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || null)
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo')) || {})
  const loading = ref(false)
  const error = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  const normalizeUser = (user) => {
    if (!user) return {}
    return {
      ...user,
      school: user.school || user.school_name,
      studentId: user.studentId || user.student_id,
      role: user.student_id === 'admin' ? 'admin' : 'user'
    }
  }

  const getErrorMessage = (err, fallback) => {
    return err?.response?.data?.message || err?.response?.data?.msg || fallback
  }

  // 登录
  const login = async (credentials) => {
    loading.value = true
    error.value = null
    try {
      const response = await authAPI.login(credentials)
      const { token: newToken, user } = response.data
      const normalizedUser = normalizeUser(user)
      
      // 存储到本地存储
      localStorage.setItem('token', newToken)
      localStorage.setItem('userInfo', JSON.stringify(normalizedUser))
      
      // 更新状态
      token.value = newToken
      userInfo.value = normalizedUser
      
      // 注意：路由跳转逻辑已移至组件中处理，Store 不再持有 router 实例
      return true
    } catch (err) {
      error.value = getErrorMessage(err, '登录失败，请检查账号密码')
      throw err
    } finally {
      loading.value = false
    }
  }

  // 注册
  const register = async (userData) => {
    loading.value = true
    error.value = null
    try {
      const response = await authAPI.register(userData)
      const { token: newToken, user } = response.data
      const normalizedUser = normalizeUser(user)
      
      // 存储到本地存储
      localStorage.setItem('token', newToken)
      localStorage.setItem('userInfo', JSON.stringify(normalizedUser))
      
      // 更新状态
      token.value = newToken
      userInfo.value = normalizedUser
      
      return true
    } catch (err) {
      error.value = getErrorMessage(err, '注册失败，请稍后重试')
      throw err
    } finally {
      loading.value = false
    }
  }

  // 退出登录
  const logout = () => {
    // 清除本地存储
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
    
    // 重置状态
    token.value = null
    userInfo.value = {}
    
    // 路由跳转由组件或拦截器处理，或者在这里抛出事件
    // 为了简单起见，这里不做跳转，调用者负责跳转
  }

  // 更新个人资料
  const updateProfile = async (profileData) => {
    loading.value = true
    error.value = null
    try {
      const response = await authAPI.updateProfile(profileData)
      const normalizedUser = normalizeUser(response.data)
      userInfo.value = normalizedUser
      localStorage.setItem('userInfo', JSON.stringify(normalizedUser))
      return true
    } catch (err) {
      error.value = getErrorMessage(err, '更新资料失败')
      throw err
    } finally {
      loading.value = false
    }
  }

  // 修改密码
  const changePassword = async (passwordData) => {
    loading.value = true
    error.value = null
    try {
      await authAPI.changePassword(passwordData)
      return true
    } catch (err) {
      error.value = getErrorMessage(err, '密码修改失败')
      throw err
    } finally {
      loading.value = false
    }
  }

  // 获取用户信息
  const getUserInfo = async () => {
    if (!token.value) return
    
    loading.value = true
    error.value = null
    try {
      const response = await authAPI.getUserInfo()
      const normalizedUser = normalizeUser(response.data)
      userInfo.value = normalizedUser
      localStorage.setItem('userInfo', JSON.stringify(normalizedUser))
    } catch (err) {
      error.value = getErrorMessage(err, '获取用户信息失败')
      // 如果获取失败，可能是token过期，清除登录状态
      if (err.response?.status === 401) {
        logout()
      }
    } finally {
      loading.value = false
    }
  }

  // 初始化时检查登录状态
  const initAuth = () => {
    if (token.value) {
      getUserInfo()
    }
  }

  return {
    token,
    userInfo,
    loading,
    error,
    isLoggedIn,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    getUserInfo,
    initAuth
  }
})
