import { View, Button } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { RootState } from '../../store'
import { getPersonaStyles, selectPersonaStyle, getCurrentPersonaStyle, getHealthProfile } from '../../services/api'
import './index.scss'

export default function PersonaPage() {
  const [styles, setStyles] = useState<any[]>([])
  const [currentStyle, setCurrentStyle] = useState('')
  const [hasProfile, setHasProfile] = useState(false)
  const userId = useSelector((state: RootState) => state.user.userId)

  useEffect(() => {
    checkProfile()
    loadStyles()
    loadCurrentStyle()
  }, [])

  const checkProfile = async () => {
    try {
      const response: any = await getHealthProfile(userId)
      if (response.status === 'success') {
        setHasProfile(true)
      }
    } catch (error) {
      setHasProfile(false)
    }
  }

  const loadStyles = async () => {
    try {
      const response: any = await getPersonaStyles()
      if (response.status === 'success') {
        setStyles(response.data)
      }
    } catch (error) {
      console.error('加载风格失败:', error)
    }
  }

  const loadCurrentStyle = async () => {
    try {
      const response: any = await getCurrentPersonaStyle(userId)
      if (response.status === 'success') {
        setCurrentStyle(response.data.style_name)
      }
    } catch (error) {
      console.error('加载当前风格失败:', error)
    }
  }

  const handleSelectStyle = async (styleName: string) => {
    if (!hasProfile) {
      Taro.showToast({
        title: '请先完成用户档案填写，再选择风格',
        icon: 'none',
        duration: 2000,
      })
      return
    }

    try {
      await selectPersonaStyle(userId, styleName)
      setCurrentStyle(styleName)
      Taro.showToast({ title: '风格设置成功！', icon: 'success' })
    } catch (error: any) {
      Taro.showToast({
        title: error.response?.data?.detail || '设置失败',
        icon: 'none',
      })
    }
  }

  return (
    <View className='persona-page'>
      <View className='page-title'>😊 人物风格</View>
      <View className='page-desc'>选择您喜欢的推送人物风格，让健康资讯更有温度</View>

      {!hasProfile && (
        <View className='warning-card'>
          ⚠️ 请先完成用户档案填写，再选择风格
        </View>
      )}

      <View className='styles-list'>
        {styles.map((style, index) => (
          <View
            key={index}
            className={`style-card ${currentStyle === style.name ? 'active' : ''}`}
            onClick={() => handleSelectStyle(style.name)}
          >
            <View className='style-name'>{style.icon} {style.name}</View>
            <View className='style-desc'>{style.description}</View>
            {currentStyle === style.name && <View className='active-tag'>已选择</View>}
          </View>
        ))}
      </View>
    </View>
  )
}




