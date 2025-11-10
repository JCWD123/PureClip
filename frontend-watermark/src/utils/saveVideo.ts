import Taro from '@tarojs/taro'

/**
 * 保存视频到相册（带授权和弹窗提示）
 * @param filePath 临时文件路径或网络地址
 * @returns Promise<void>
 */
export const saveVideoWithAuth = (filePath: string): Promise<void> => {
  return new Promise<void>((resolve, reject) => {
    // 先检查是否已授权
    Taro.getSetting({
      success: (settingRes) => {
        const authStatus = settingRes.authSetting['scope.writePhotosAlbum']
        
        // 情况1: 已授权，直接保存
        if (authStatus === true) {
          performSaveVideo(filePath, resolve, reject)
          return
        }
        
        // 情况2: 未授权或第一次请求，显示授权弹窗
        if (authStatus === undefined || authStatus === false) {
          showAuthModal(filePath, authStatus, resolve, reject)
        }
      },
      fail: (err) => {
        console.error('获取授权状态失败:', err)
        // 即使获取失败，也尝试直接保存
        showAuthModal(filePath, undefined, resolve, reject)
      }
    })
  })
}

/**
 * 保存图片到相册（带授权和弹窗提示）
 * @param filePath 临时文件路径或网络地址
 * @returns Promise<void>
 */
export const saveImageWithAuth = (filePath: string): Promise<void> => {
  return new Promise<void>((resolve, reject) => {
    // 先检查是否已授权
    Taro.getSetting({
      success: (settingRes) => {
        const authStatus = settingRes.authSetting['scope.writePhotosAlbum']
        
        // 情况1: 已授权，直接保存
        if (authStatus === true) {
          performSaveImage(filePath, resolve, reject)
          return
        }
        
        // 情况2: 未授权或第一次请求，显示授权弹窗
        if (authStatus === undefined || authStatus === false) {
          showAuthModalForImage(filePath, authStatus, resolve, reject)
        }
      },
      fail: (err) => {
        console.error('获取授权状态失败:', err)
        // 即使获取失败，也尝试直接保存
        showAuthModalForImage(filePath, undefined, resolve, reject)
      }
    })
  })
}

/**
 * 显示授权弹窗（视频）
 */
function showAuthModal(
  filePath: string,
  authStatus: boolean | undefined,
  resolve: () => void,
  reject: (reason?: any) => void
) {
  // 如果是第一次请求（undefined），显示友好的说明弹窗
  if (authStatus === undefined) {
    Taro.showModal({
      title: '保存视频',
      content: '需要您的授权才能将视频保存到相册，是否允许？',
      confirmText: '允许',
      cancelText: '暂不',
      success: (res) => {
        if (res.confirm) {
          // 请求相册权限
          Taro.authorize({
            scope: 'scope.writePhotosAlbum',
            success: () => {
              performSaveVideo(filePath, resolve, reject)
            },
            fail: (err) => {
              console.error('授权失败:', err)
              Taro.showToast({ title: '授权失败', icon: 'none' })
              reject('用户拒绝授权')
            }
          })
        } else {
          Taro.showToast({ title: '已取消', icon: 'none' })
          reject('用户取消保存')
        }
      }
    })
  } 
  // 如果是之前拒绝过（false），引导用户去设置页面
  else if (authStatus === false) {
    Taro.showModal({
      title: '权限提示',
      content: '保存视频需要访问您的相册权限，请在设置中开启相册权限。',
      confirmText: '去设置',
      cancelText: '取消',
      success: (settingRes) => {
        if (settingRes.confirm) {
          Taro.openSetting({
            success: (openRes) => {
              if (openRes.authSetting['scope.writePhotosAlbum']) {
                // 用户在设置页面开启了权限，直接保存
                performSaveVideo(filePath, resolve, reject)
              } else {
                Taro.showToast({ title: '未开启权限', icon: 'none' })
                reject('用户未开启权限')
              }
            },
            fail: (err) => {
              console.error('打开设置页面失败:', err)
              reject('打开设置失败')
            }
          })
        } else {
          reject('用户拒绝前往设置')
        }
      }
    })
  }
}

/**
 * 显示授权弹窗（图片）
 */
function showAuthModalForImage(
  filePath: string,
  authStatus: boolean | undefined,
  resolve: () => void,
  reject: (reason?: any) => void
) {
  // 如果是第一次请求（undefined），显示友好的说明弹窗
  if (authStatus === undefined) {
    Taro.showModal({
      title: '保存图片',
      content: '需要您的授权才能将图片保存到相册，是否允许？',
      confirmText: '允许',
      cancelText: '暂不',
      success: (res) => {
        if (res.confirm) {
          // 请求相册权限
          Taro.authorize({
            scope: 'scope.writePhotosAlbum',
            success: () => {
              performSaveImage(filePath, resolve, reject)
            },
            fail: (err) => {
              console.error('授权失败:', err)
              Taro.showToast({ title: '授权失败', icon: 'none' })
              reject('用户拒绝授权')
            }
          })
        } else {
          Taro.showToast({ title: '已取消', icon: 'none' })
          reject('用户取消保存')
        }
      }
    })
  } 
  // 如果是之前拒绝过（false），引导用户去设置页面
  else if (authStatus === false) {
    Taro.showModal({
      title: '权限提示',
      content: '保存图片需要访问您的相册权限，请在设置中开启相册权限。',
      confirmText: '去设置',
      cancelText: '取消',
      success: (settingRes) => {
        if (settingRes.confirm) {
          Taro.openSetting({
            success: (openRes) => {
              if (openRes.authSetting['scope.writePhotosAlbum']) {
                // 用户在设置页面开启了权限，直接保存
                performSaveImage(filePath, resolve, reject)
              } else {
                Taro.showToast({ title: '未开启权限', icon: 'none' })
                reject('用户未开启权限')
              }
            },
            fail: (err) => {
              console.error('打开设置页面失败:', err)
              reject('打开设置失败')
            }
          })
        } else {
          reject('用户拒绝前往设置')
        }
      }
    })
  }
}

/**
 * 执行保存视频操作
 */
function performSaveVideo(
  filePath: string,
  resolve: () => void,
  reject: (reason?: any) => void
) {
  Taro.showLoading({ title: '正在保存...', mask: true })
  
  Taro.saveVideoToPhotosAlbum({
    filePath,
    success: () => {
      Taro.hideLoading()
      Taro.showToast({
        title: '已保存到相册',
        icon: 'success',
        duration: 2000
      })
      console.log('✅ 视频保存成功:', filePath)
      resolve()
    },
    fail: (err) => {
      Taro.hideLoading()
      console.error('❌ 视频保存失败:', err)
      
      // 错误处理
      let errorMsg = '保存失败'
      if (err.errMsg) {
        if (err.errMsg.includes('auth')) {
          errorMsg = '保存失败，请重新授权'
        } else if (err.errMsg.includes('cancel')) {
          errorMsg = '保存已取消'
        } else if (err.errMsg.includes('fail')) {
          errorMsg = '保存失败，请稍后重试'
        }
      }
      
      Taro.showToast({
        title: errorMsg,
        icon: 'none',
        duration: 2000
      })
      reject(err)
    }
  })
}

/**
 * 执行保存图片操作
 */
function performSaveImage(
  filePath: string,
  resolve: () => void,
  reject: (reason?: any) => void
) {
  Taro.showLoading({ title: '正在保存...', mask: true })
  
  Taro.saveImageToPhotosAlbum({
    filePath,
    success: () => {
      Taro.hideLoading()
      Taro.showToast({
        title: '已保存到相册',
        icon: 'success',
        duration: 2000
      })
      console.log('✅ 图片保存成功:', filePath)
      resolve()
    },
    fail: (err) => {
      Taro.hideLoading()
      console.error('❌ 图片保存失败:', err)
      
      // 错误处理
      let errorMsg = '保存失败'
      if (err.errMsg) {
        if (err.errMsg.includes('auth')) {
          errorMsg = '保存失败，请重新授权'
        } else if (err.errMsg.includes('cancel')) {
          errorMsg = '保存已取消'
        } else if (err.errMsg.includes('fail')) {
          errorMsg = '保存失败，请稍后重试'
        }
      }
      
      Taro.showToast({
        title: errorMsg,
        icon: 'none',
        duration: 2000
      })
      reject(err)
    }
  })
}

/**
 * 检查隐私协议是否需要确认（微信2.0隐私协议）
 * @returns Promise<boolean> 是否需要弹出隐私协议
 */
export const checkPrivacyAgreement = (): Promise<boolean> => {
  return new Promise((resolve) => {
    // 检查是否支持隐私协议 API
    if (typeof Taro.getPrivacySetting === 'function') {
      Taro.getPrivacySetting({
        success: (res) => {
          console.log('隐私协议状态:', res)
          // needAuthorization: true 表示需要用户确认隐私协议
          // privacyContractName: 隐私协议名称
          if (res.needAuthorization) {
            console.warn('⚠️ 用户未同意隐私协议，需要弹出隐私弹窗')
            resolve(true)
          } else {
            console.log('✅ 用户已同意隐私协议')
            resolve(false)
          }
        },
        fail: (err) => {
          console.error('获取隐私设置失败:', err)
          // 如果获取失败，默认不需要弹出（兼容旧版本）
          resolve(false)
        }
      })
    } else {
      // 不支持隐私协议 API（旧版本微信），默认不需要弹出
      console.log('当前微信版本不支持隐私协议 API')
      resolve(false)
    }
  })
}

/**
 * 全面的权限和隐私检查
 * @returns Promise<'authorized' | 'need_auth' | 'need_privacy'>
 */
export const checkAllPermissions = async (): Promise<'authorized' | 'need_auth' | 'need_privacy'> => {
  try {
    // 1. 先检查隐私协议
    const needPrivacy = await checkPrivacyAgreement()
    if (needPrivacy) {
      return 'need_privacy'
    }
    
    // 2. 再检查相册权限
    const settingRes = await Taro.getSetting()
    const authStatus = settingRes.authSetting['scope.writePhotosAlbum']
    
    if (authStatus === true) {
      return 'authorized'
    } else {
      return 'need_auth'
    }
  } catch (err) {
    console.error('权限检查失败:', err)
    return 'need_auth'
  }
}

