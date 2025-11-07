import { View, Button, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { RootState } from '../../store'
import { pushMealReminder, getPushHistory } from '../../services/api'
import './index.scss'

export default function MealPage() {
  const [loadingStates, setLoadingStates] = useState({
    breakfast: false,
    lunch: false,
    dinner: false,
  })
  const [latestContent, setLatestContent] = useState('')
  const [history, setHistory] = useState<any[]>([])
  const userId = useSelector((state: RootState) => state.user.userId)

  const mealTypes = {
    breakfast: { label: '早餐', icon: '🥐', type: 'breakfast' },
    lunch: { label: '午餐', icon: '🍜', type: 'lunch' },
    dinner: { label: '晚餐', icon: '🍱', type: 'dinner' },
  }

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const response: any = await getPushHistory(userId, 'meal', 10)
      if (response.status === 'success') {
        setHistory(response.data)
        if (response.data.length > 0) {
          setLatestContent(response.data[0].content)
        }
      }
    } catch (error) {
      console.error('加载历史失败:', error)
    }
  }

  const handlePush = async (mealType: string) => {
    setLoadingStates((prev) => ({ ...prev, [mealType]: true }))
    try {
      const response: any = await pushMealReminder(userId, mealType)
      if (response.status === 'success') {
        setLatestContent(response.content)
        Taro.showToast({ title: '推送成功！', icon: 'success' })
        loadHistory()
      }
    } catch (error: any) {
      Taro.showToast({
        title: error.response?.data?.detail || '推送失败',
        icon: 'none',
      })
    } finally {
      setLoadingStates((prev) => ({ ...prev, [mealType]: false }))
    }
  }

  return (
    <View className='meal-page'>
      <View className='page-title'>🍽️ 饮食提醒</View>
      <View className='page-desc'>系统会根据您的健康状况和饮食习惯，在用餐时间推送饮食建议</View>

      <View className='push-section'>
        <View className='section-title'>获取饮食提醒</View>
        {Object.entries(mealTypes).map(([key, value]) => (
          <Button
            key={key}
            type='primary'
            loading={loadingStates[key]}
            onClick={() => handlePush(value.type)}
            className='meal-button'
          >
            {value.icon} {value.label}提醒
          </Button>
        ))}
      </View>

      {latestContent && (
        <View className='latest-content'>
          <View className='section-title'>最新推送内容</View>
          <View className='content-card'>{latestContent}</View>
        </View>
      )}

      {history.length > 0 && (
        <View className='history-section'>
          <View className='section-title'>历史推送</View>
          <ScrollView scrollY className='history-list'>
            {history.map((item, index) => (
              <View key={index} className='history-item'>
                <View className='time'>{item.push_time}</View>
                <View className='content'>{item.content}</View>
              </View>
            ))}
          </ScrollView>
        </View>
      )}
    </View>
  )
}




