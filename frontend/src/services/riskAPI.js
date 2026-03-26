import api from './api'

/**
 * 获取安全提示
 */
export const getSafetyTips = () => {
  return api.get('/risk/safety-tips')
}

/**
 * 检查内容安全性
 */
export const checkContentSafety = (content) => {
  return api.post('/risk/check-content', { content })
}

/**
 * 记录用户行为
 */
export const logUserAction = (actionType, targetId = null, content = null) => {
  return api.post('/risk/log-action', {
    action_type: actionType,
    target_id: targetId,
    content: content
  })
}

/**
 * 获取用户风险标签
 */
export const getUserRiskTags = () => {
  return api.get('/risk/user-tags')
}
