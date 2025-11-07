import { View, Button, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { RootState } from '../../store'
import { pushRestReminder, getPushHistory } from '../../services/api'
import './index.scss'

export default function RestPage() {
  const [loadingStates, setLoadingStates] = useState({
    morning: false,
    noon: false,
    night: false,
  })
  const [latestContent, setLatestContent] = useState('')
  const [history, setHistory] = useState<any[]>([])
  const userId = useSelector((state: RootState) => state.user.userId)

  const timeSlots = {
    morning: { label: '早晨 7:00', icon: '🌅', type: 'morning' },
    noon: { label: '中午 13:00', icon: '☀️', type: 'noon' },
    night: { label: '夜晚 23:00', icon: '🌙', type: 'night' },
  }

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const response: any = await getPushHistory(userId, 'rest', 10)
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

  const handlePush = async (timeType: string) => {
    setLoadingStates((prev) => ({ ...prev, [timeType]: true }))
    try {
      const response: any = await pushRestReminder(userId, timeType)
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
      setLoadingStates((prev) => ({ ...prev, [timeType]: false }))
    }
  }

  return (
    <View className='rest-page'>
      <View className='page-title'>⏰ 作息提醒</View>
      <View className='page-desc'>系统会根据您的生活习惯，在每天的关键时间点推送作息提醒</View>

      <View className='push-section'>
        <View className='section-title'>获取作息提醒</View>
        {Object.entries(timeSlots).map(([key, value]) => (
          <Button
            key={key}
            type='primary'
            loading={loadingStates[key]}
            onClick={() => handlePush(value.type)}
            className='time-button'
          >
            {value.icon} {value.label}
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




