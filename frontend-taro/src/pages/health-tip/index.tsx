import { View, Button, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useState, useEffect } from 'react'
import { useSelector } from 'react-redux'
import { RootState } from '../../store'
import { pushHealthTip, getPushHistory } from '../../services/api'
import './index.scss'

export default function HealthTipPage() {
  const [loading, setLoading] = useState(false)
  const [latestContent, setLatestContent] = useState('')
  const [history, setHistory] = useState<any[]>([])
  const userId = useSelector((state: RootState) => state.user.userId)

  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async () => {
    try {
      const response: any = await getPushHistory(userId, 'health_tip', 10)
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

  const handlePush = async () => {
    setLoading(true)
    try {
      const response: any = await pushHealthTip(userId)
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
      setLoading(false)
    }
  }

  return (
    <View className='health-tip-page'>
      <View className='page-title'>💚 养生妙招</View>
      <View className='page-desc'>系统会在每天下午2:00推送个性化的养生建议</View>

      <View className='push-section'>
        <View className='section-title'>获取养生妙招</View>
        <Button type='primary' loading={loading} onClick={handlePush} className='push-button'>
          🌿 获取今日养生建议
        </Button>
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




