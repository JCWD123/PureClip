import { request } from '../utils/request'

// ============ 健康档案相关API ============

export interface BasicInfo {
  nickname: string
  birth_date: string
  age: number
  gender: string
  height: number
  weight: number
  blood_type?: string
}

export interface HealthInfo {
  lifestyle_habits: string[]
  allergies: string[]
  medical_history: string[]
  adverse_reactions: string[]
  family_history: string[]
  surgery_history: Array<{ name: string; date: string }>
}

export interface OtherInfo {
  vaccination: Array<{ name: string; date: string }>
  menstruation?: any
  fertility?: any
  other_notes?: string
}

export interface HealthProfile {
  user_id: string
  basic_info: BasicInfo
  health_info: HealthInfo
  other_info: OtherInfo
  persona_style?: string
  location?: { province: string; city: string }
}

// 创建健康档案
export const createHealthProfile = (data: HealthProfile) => {
  return request('/health-profile', {
    method: 'POST',
    data,
  })
}

// 获取健康档案
export const getHealthProfile = (userId: string) => {
  return request(`/health-profile/${userId}`)
}

// 更新健康档案
export const updateHealthProfile = (userId: string, data: any) => {
  return request(`/health-profile/${userId}`, {
    method: 'PUT',
    data,
  })
}

// 设置用户地区
export const setUserLocation = (userId: string, location: { province: string; city: string }) => {
  return request(`/health-profile/${userId}/location`, {
    method: 'POST',
    data: location,
  })
}

// ============ 人物风格相关API ============

// 获取所有人物风格
export const getPersonaStyles = () => {
  return request('/persona-styles')
}

// 选择人物风格
export const selectPersonaStyle = (userId: string, styleName: string) => {
  return request(`/persona-styles/${userId}/select`, {
    method: 'POST',
    data: { style_name: styleName },
  })
}

// 获取当前人物风格
export const getCurrentPersonaStyle = (userId: string) => {
  return request(`/persona-styles/${userId}/current`)
}

// ============ 健康推送相关API ============

// 推送作息提醒
export const pushRestReminder = (userId: string, timeType: string) => {
  return request(`/push/rest/${userId}?time_type=${timeType}`, {
    method: 'POST',
  })
}

// 推送饮食提醒
export const pushMealReminder = (userId: string, mealType: string) => {
  return request(`/push/meal/${userId}?meal_type=${mealType}`, {
    method: 'POST',
  })
}

// 推送天气提醒
export const pushWeatherReminder = (userId: string) => {
  return request(`/push/weather/${userId}`, {
    method: 'POST',
  })
}

// 推送养生妙招
export const pushHealthTip = (userId: string) => {
  return request(`/push/health-tip/${userId}`, {
    method: 'POST',
  })
}

// 获取推送历史
export const getPushHistory = (userId: string, pushType?: string, limit: number = 20) => {
  const params = new URLSearchParams()
  if (pushType) params.append('push_type', pushType)
  params.append('limit', limit.toString())
  return request(`/push/history/${userId}?${params.toString()}`)
}

// 标记推送为已读
export const markPushAsRead = (pushId: string, userId: string) => {
  return request(`/push/history/${pushId}/read?user_id=${userId}`, {
    method: 'PUT',
  })
}




