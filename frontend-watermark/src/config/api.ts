// API配置
export const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.pureclip.arbismart.cloud/api'  // 生产环境API地址
  : 'http://localhost:8001/api'  // 开发环境API地址

// API端点
export const API_ENDPOINTS = {
  // 任务管理
  CREATE_TASK: '/tasks',
  GET_TASK: '/tasks',
  LIST_TASKS: '/tasks',
  DELETE_TASK: '/tasks',
  
  // 历史记录
  GET_HISTORY: '/history',
  DELETE_HISTORY: '/history'
}



