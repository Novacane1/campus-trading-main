import api from './api'

/**
 * 获取常用地点列表
 */
export const getCommonLocations = () => {
  return api.get('/time-location/common-locations')
}

/**
 * 获取预定义时间段
 */
export const getTimeSlots = () => {
  return api.get('/time-location/time-slots')
}

/**
 * 计算时空匹配度
 */
export const calculateMatch = (itemId) => {
  return api.post('/time-location/match', { item_id: itemId })
}

/**
 * 获取下一个可用时间
 */
export const getNextAvailableTime = (timeSlots) => {
  return api.post('/time-location/next-available', { time_slots: timeSlots })
}

/**
 * 验证时间段格式
 */
export const validateTimeSlot = (timeSlot) => {
  return api.post('/time-location/validate-time-slot', { time_slot: timeSlot })
}
