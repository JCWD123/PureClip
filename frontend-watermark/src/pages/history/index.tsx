import { View, Button, ScrollView } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useEffect, useState } from 'react'
import { historyApi } from '../../services/api'
import './index.scss'

export default function History() {
  const [historyList, setHistoryList] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      setLoading(true)
      const result = await historyApi.getHistory({
        user_id: 'test_user_001', // 这里应该从用户系统获取
        limit: 50
      })
      setHistoryList(result.history || [])
    } catch (error) {
      console.error('获取历史记录失败:', error)
      Taro.showToast({
        title: '获取历史记录失败',
        icon: 'none'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleCopyUrl = (url: string) => {
    Taro.setClipboardData({
      data: url,
      success: () => {
        Taro.showToast({
          title: '链接已复制',
          icon: 'success'
        })
      }
    })
  }

  const handleDelete = async (historyId: string) => {
    Taro.showModal({
      title: '提示',
      content: '确定要删除这条历史记录吗？',
      success: async (res) => {
        if (res.confirm) {
          try {
            await historyApi.deleteHistory(historyId)
            Taro.showToast({
              title: '删除成功',
              icon: 'success'
            })
            fetchHistory()
          } catch (error) {
            console.error('删除失败:', error)
            Taro.showToast({
              title: '删除失败',
              icon: 'none'
            })
          }
        }
      }
    })
  }

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  }

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  const getMethodText = (method: string) => {
    const methodMap: Record<string, string> = {
      crop: '裁剪',
      blur: '模糊',
      cover: '覆盖',
      inpaint: '填充'
    }
    return methodMap[method] || method
  }

  if (loading) {
    return (
      <View className='history-page'>
        <View className='loading'>加载中...</View>
      </View>
    )
  }

  if (historyList.length === 0) {
    return (
      <View className='history-page'>
        <View className='empty-state'>
          <View className='empty-icon'>📝</View>
          <View className='empty-text'>暂无历史记录</View>
          <Button
            className='goto-home-btn'
            onClick={() => Taro.switchTab({ url: '/pages/index/index' })}
          >
            去处理视频
          </Button>
        </View>
      </View>
    )
  }

  return (
    <View className='history-page'>
      <ScrollView scrollY className='history-list'>
        {historyList.map((item) => (
          <View key={item.history_id} className='history-item'>
            <View className='item-header'>
              <View className='media-type'>
                {item.media_type === 'video' ? '🎬 视频' : '🖼️ 图片'}
              </View>
              <View className='method-badge'>{getMethodText(item.method)}</View>
            </View>

            <View className='item-info'>
              <View className='info-row'>
                <View className='info-label'>处理时间：</View>
                <View className='info-value'>{formatDate(item.created_at)}</View>
              </View>
              <View className='info-row'>
                <View className='info-label'>文件大小：</View>
                <View className='info-value'>{formatFileSize(item.file_size)}</View>
              </View>
              <View className='info-row'>
                <View className='info-label'>耗时：</View>
                <View className='info-value'>{item.process_time.toFixed(2)}秒</View>
              </View>
            </View>

            <View className='item-actions'>
              <Button
                className='action-btn copy'
                onClick={() => handleCopyUrl(item.result_url)}
              >
                复制链接
              </Button>
              <Button
                className='action-btn delete'
                onClick={() => handleDelete(item.history_id)}
              >
                删除
              </Button>
            </View>
          </View>
        ))}
      </ScrollView>
    </View>
  )
}





