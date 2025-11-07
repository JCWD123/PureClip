import Taro from '@tarojs/taro'
import { API_BASE_URL } from '../config/api'

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: any
}

export const request = async (url: string, options: RequestOptions = {}) => {
  const { method = 'GET', data, header = {} } = options

  try {
    Taro.showLoading({ title: '加载中...' })

    const response = await Taro.request({
      url: `${API_BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...header,
      },
    })

    Taro.hideLoading()

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response.data
    } else {
      // 创建包含statusCode的错误对象
      const error: any = new Error(`请求失败: ${response.statusCode}`)
      error.statusCode = response.statusCode
      error.status = response.statusCode
      error.response = response
      throw error
    }
  } catch (error: any) {
    Taro.hideLoading()
    
    // 如果错误已经有statusCode，说明是HTTP错误，不显示Toast
    // 让调用方自己处理
    if (!error.statusCode && !error.status) {
      // 只有真正的网络错误才显示Toast
      Taro.showToast({
        title: '网络请求失败',
        icon: 'none',
      })
    }
    
    throw error
  }
}

