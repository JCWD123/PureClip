import { View, Button, Switch } from '@tarojs/components'
import Taro, { useShareAppMessage } from '@tarojs/taro'
import { useState, useEffect } from 'react'
import { getUserId, getUserInfo } from '../../utils/user'
import './index.scss'

export default function Profile() {
  const [showSmartTips, setShowSmartTips] = useState(true)
  const [userId, setUserId] = useState('')
  const [userIdShort, setUserIdShort] = useState('')

  // ✅ 页面分享配置（Hooks 写法）
  useShareAppMessage(() => {
    return {
      title: 'PureClip去水印 - 快速去除视频水印',
      path: '/pages/index/index'
    }
  })

  useEffect(() => {
    // 从本地存储加载设置
    const savedTips = Taro.getStorageSync('showSmartTips')
    if (savedTips !== undefined) {
      setShowSmartTips(savedTips)
    }

    // 获取用户ID
    getUserId().then(id => {
      setUserId(id)
      // 显示ID的前8位（用于界面展示）
      setUserIdShort(id.substring(0, 8))
      console.log('✅ 个人中心 - 用户信息:', getUserInfo())
    })
  }, [])

  const handleSmartTipsChange = (e: any) => {
    const value = e.detail.value
    setShowSmartTips(value)
    Taro.setStorageSync('showSmartTips', value)
    
    Taro.showToast({
      title: value ? '已开启智能提示' : '已关闭智能提示',
      icon: 'none',
      duration: 1500
    })
  }

  const handleHistoryClick = () => {
    Taro.switchTab({
      url: '/pages/history/index'
    })
  }

  const handleHelpClick = () => {
    Taro.showModal({
      title: '使用帮助',
      content: '1. 复制视频链接\n2. 粘贴到首页输入框\n3. 点击"一键去水印"\n4. 等待2-5秒完成解析\n5. 播放或下载无水印视频\n\n支持平台：抖音、快手、小红书、百度等',
      confirmText: '知道了',
      showCancel: false
    })
  }

  return (
    <View className='profile-page'>
      {/* 用户信息区域 */}
      <View className='user-header'>
        <View className='user-avatar'>
          <View className='avatar-placeholder'>👤</View>
        </View>
        <View className='user-info'>
          <View className='user-id'>ID: {userIdShort || '加载中...'}</View>
        </View>
      </View>

      {/* 功能列表 */}
      <View className='menu-container'>
        {/* 解析记录 */}
        <View className='menu-item' onClick={handleHistoryClick}>
          <View className='menu-left'>
            <View className='menu-icon' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
              📋
            </View>
            <View className='menu-text'>解析记录</View>
          </View>
          <View className='menu-arrow'>›</View>
        </View>

        {/* 使用帮助 */}
        <View className='menu-item' onClick={handleHelpClick}>
          <View className='menu-left'>
            <View className='menu-icon' style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);'>
              ❓
            </View>
            <View className='menu-text'>使用帮助</View>
          </View>
          <View className='menu-arrow'>›</View>
        </View>

        {/* 分享 - 使用微信原生分享 */}
        <Button className='menu-item-button' openType='share'>
          <View className='menu-item'>
            <View className='menu-left'>
              <View className='menu-icon' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'>
                📤
              </View>
              <View className='menu-text'>分享</View>
            </View>
            <View className='menu-arrow'>›</View>
          </View>
        </Button>

        {/* 联系客服 - 使用微信官方客服 */}
        <Button className='menu-item-button' openType='contact'>
          <View className='menu-item'>
            <View className='menu-left'>
              <View className='menu-icon' style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);'>
                👥
              </View>
              <View className='menu-text'>联系客服</View>
            </View>
            <View className='menu-arrow'>›</View>
          </View>
        </Button>
      </View>

      {/* 智能提示弹框 */}
      <View className='settings-container'>
        <View className='setting-item'>
          <View className='setting-left'>
            <View className='setting-icon'>💡</View>
            <View className='setting-text'>智能提示弹框</View>
          </View>
          <Switch
            className='setting-switch'
            checked={showSmartTips}
            onChange={handleSmartTipsChange}
            color='#667eea'
          />
        </View>
      </View>

      {/* 版本信息 */}
      <View className='footer-info'>
        <View className='version-text'>PureClip v1.0.0</View>
        <View className='copyright-text'>快速去水印，简单高效</View>
      </View>
    </View>
  )
}

