import { request } from '../utils/request'
import { API_ENDPOINTS } from '../config/api'

// 任务相关接口
export const taskApi = {
  // 创建任务
  createTask: (data: {
    url: string
    media_type: 'video' | 'image'
    method: 'crop' | 'blur' | 'cover' | 'inpaint'
    watermark_region?: { x: number; y: number; width: number; height: number }
    user_id?: string
  }) => {
    return request(API_ENDPOINTS.CREATE_TASK, {
      method: 'POST',
      data
    })
  },

  // 查询任务状态
  getTask: (taskId: string) => {
    return request(`${API_ENDPOINTS.GET_TASK}/${taskId}`, {
      method: 'GET',
      showLoading: false
    })
  },

  // 查询任务列表
  listTasks: (params?: {
    user_id?: string
    status?: string
    limit?: number
    skip?: number
  }) => {
    const query = new URLSearchParams(params as any).toString()
    return request(`${API_ENDPOINTS.LIST_TASKS}?${query}`, {
      method: 'GET'
    })
  },

  // 删除任务
  deleteTask: (taskId: string) => {
    return request(`${API_ENDPOINTS.DELETE_TASK}/${taskId}`, {
      method: 'DELETE'
    })
  }
}

// 历史记录相关接口
export const historyApi = {
  // 获取历史记录
  getHistory: (params: {
    user_id: string
    limit?: number
    skip?: number
  }) => {
    const query = new URLSearchParams(params as any).toString()
    return request(`${API_ENDPOINTS.GET_HISTORY}?${query}`, {
      method: 'GET'
    })
  },

  // 删除历史记录
  deleteHistory: (historyId: string) => {
    return request(`${API_ENDPOINTS.DELETE_HISTORY}/${historyId}`, {
      method: 'DELETE'
    })
  }
}






