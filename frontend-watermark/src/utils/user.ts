/**
 * 用户身份管理工具
 * 用于获取和管理微信小程序用户的唯一标识
 */

import Taro from '@tarojs/taro'

const USER_ID_KEY = 'pureclip_user_id'
const OPENID_KEY = 'pureclip_openid'

/**
 * 获取用户唯一标识
 * 优先级: OpenID > 缓存的UUID > 新生成的UUID
 */
export async function getUserId(): Promise<string> {
  try {
    // 1. 尝试从缓存获取 OpenID
    const cachedOpenId = Taro.getStorageSync(OPENID_KEY)
    if (cachedOpenId) {
      console.log('✅ 使用缓存的 OpenID:', cachedOpenId)
      return cachedOpenId
    }

    // 2. 尝试从缓存获取 UUID
    const cachedUserId = Taro.getStorageSync(USER_ID_KEY)
    if (cachedUserId) {
      console.log('✅ 使用缓存的 UUID:', cachedUserId)
      return cachedUserId
    }

    // 3. 生成新的 UUID 并缓存
    const newUserId = generateUUID()
    Taro.setStorageSync(USER_ID_KEY, newUserId)
    console.log('✅ 生成新的 UUID:', newUserId)
    return newUserId
  } catch (error) {
    console.error('❌ 获取用户ID失败:', error)
    // 如果所有方法都失败，生成临时ID（不缓存）
    return generateUUID()
  }
}

/**
 * 微信登录获取 OpenID
 * 注意: 需要后端提供登录接口
 */
export async function wxLogin(): Promise<string | null> {
  try {
    console.log('🔐 开始微信登录...')
    
    // 1. 获取微信登录凭证 code
    const loginResult = await Taro.login()
    if (!loginResult.code) {
      throw new Error('获取登录凭证失败')
    }
    console.log('✅ 获取到 code:', loginResult.code)

    // 2. 调用后端接口，用 code 换取 openid
    // TODO: 需要后端实现 /api/user/login 接口
    const response = await Taro.request({
      url: `${getApiBaseUrl()}/user/login`,
      method: 'POST',
      data: {
        code: loginResult.code
      }
    })

    if (response.statusCode === 200 && response.data.openid) {
      const openid = response.data.openid
      
      // 3. 缓存 OpenID
      Taro.setStorageSync(OPENID_KEY, openid)
      Taro.setStorageSync(USER_ID_KEY, openid)
      
      console.log('✅ 登录成功，OpenID:', openid)
      return openid
    } else {
      throw new Error('后端返回数据异常')
    }
  } catch (error) {
    console.error('❌ 微信登录失败:', error)
    
    // 如果登录失败，使用 UUID 作为临时用户标识
    const fallbackId = await getUserId()
    console.warn('⚠️ 使用备用用户ID:', fallbackId)
    return fallbackId
  }
}

/**
 * 生成 UUID
 */
function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0
    const v = c === 'x' ? r : (r & 0x3 | 0x8)
    return v.toString(16)
  })
}

/**
 * 获取 API 基础地址
 */
function getApiBaseUrl(): string {
  // 根据环境返回不同的 API 地址
  return process.env.NODE_ENV === 'production' 
    ? 'https://api.pureclip.arbismart.cloud/api'
    : 'http://localhost:8001/api'
}

/**
 * 清除用户信息（用于退出登录）
 */
export function clearUserInfo(): void {
  try {
    Taro.removeStorageSync(OPENID_KEY)
    Taro.removeStorageSync(USER_ID_KEY)
    console.log('✅ 用户信息已清除')
  } catch (error) {
    console.error('❌ 清除用户信息失败:', error)
  }
}

/**
 * 检查是否已登录（有 OpenID）
 */
export function isLoggedIn(): boolean {
  const openid = Taro.getStorageSync(OPENID_KEY)
  return !!openid
}

/**
 * 获取用户信息（用于调试）
 */
export function getUserInfo() {
  return {
    openid: Taro.getStorageSync(OPENID_KEY),
    userId: Taro.getStorageSync(USER_ID_KEY),
    isLoggedIn: isLoggedIn()
  }
}


