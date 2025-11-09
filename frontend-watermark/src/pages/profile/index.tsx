import { View, Button, Switch } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useState, useEffect } from 'react'
import './index.scss'

export default function Profile() {
  const [showSmartTips, setShowSmartTips] = useState(true)
  const [userId] = useState('8759892') // 这里应该从用户系统获取

  useEffect(() => {
    // 从本地存储加载设置
    const savedTips = Taro.getStorageSync('showSmartTips')
    if (savedTips !== undefined) {
      setShowSmartTips(savedTips)
    }
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

  const handleShareClick = () => {
    Taro.showShareMenu({
      withShareTicket: true,
      showShareItems: ['wechatFriends', 'wechatMoment']
    })
    
    Taro.showToast({
      title: '点击右上角分享',
      icon: 'none',
      duration: 2000
    })
  }

  const handleContactClick = () => {
    Taro.showModal({
      title: '联系客服',
      content: '客服微信：pureclip001\n\n或点击"复制"按钮复制微信号，然后在微信中添加好友',
      confirmText: '复制微信号',
      cancelText: '取消',
      success: (res) => {
        if (res.confirm) {
          Taro.setClipboardData({
            data: 'pureclip001',
            success: () => {
              Taro.showToast({
                title: '微信号已复制',
                icon: 'success'
              })
            }
          })
        }
      }
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
          <View className='user-id'>ID: {userId}</View>
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

        {/* 分享 */}
        <View className='menu-item' onClick={handleShareClick}>
          <View className='menu-left'>
            <View className='menu-icon' style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);'>
              📤
            </View>
            <View className='menu-text'>分享</View>
          </View>
          <View className='menu-arrow'>›</View>
        </View>

        {/* 联系客服 */}
        <View className='menu-item' onClick={handleContactClick}>
          <View className='menu-left'>
            <View className='menu-icon' style='background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);'>
              👥
            </View>
            <View className='menu-text'>联系客服</View>
          </View>
          <View className='menu-arrow'>›</View>
        </View>
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

