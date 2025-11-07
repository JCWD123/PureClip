import { View, Button, Video, Image } from '@tarojs/components'
import Taro, { useRouter } from '@tarojs/taro'
import { useEffect, useState } from 'react'
import { taskApi } from '../../services/api'
import './index.scss'

export default function Result() {
  const router = useRouter()
  const { taskId } = router.params
  const [task, setTask] = useState<any>(null)
  const [polling, setPolling] = useState(true)

  useEffect(() => {
    if (taskId) {
      fetchTaskStatus()
    }
  }, [taskId])

  useEffect(() => {
    if (polling && taskId) {
      const timer = setInterval(() => {
        fetchTaskStatus()
      }, 2000) // 每2秒轮询一次

      return () => clearInterval(timer)
    }
  }, [polling, taskId])

  const fetchTaskStatus = async () => {
    try {
      const result = await taskApi.getTask(taskId!)
      setTask(result)

      // 如果任务完成或失败，停止轮询
      if (result.status === 'completed' || result.status === 'failed') {
        setPolling(false)
      }
    } catch (error) {
      console.error('查询任务失败:', error)
    }
  }

  const handleCopyUrl = () => {
    if (task?.result_url) {
      Taro.setClipboardData({
        data: task.result_url,
        success: () => {
          Taro.showToast({
            title: '链接已复制',
            icon: 'success'
          })
        }
      })
    }
  }

  const handleDownload = () => {
    if (task?.result_url) {
      Taro.downloadFile({
        url: task.result_url,
        success: (res) => {
          if (res.statusCode === 200) {
            Taro.showToast({
              title: '下载成功',
              icon: 'success'
            })
          }
        }
      })
    }
  }

  const handleBackHome = () => {
    Taro.navigateBack()
  }

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      pending: '等待处理',
      downloading: '下载中',
      processing: '处理中',
      uploading: '上传中',
      completed: '处理完成',
      failed: '处理失败'
    }
    return statusMap[status] || status
  }

  const getStatusColor = (status: string) => {
    const colorMap: Record<string, string> = {
      pending: '#ffa500',
      downloading: '#1890ff',
      processing: '#1890ff',
      uploading: '#1890ff',
      completed: '#52c41a',
      failed: '#f5222d'
    }
    return colorMap[status] || '#999'
  }

  if (!task) {
    return (
      <View className='result-page'>
        <View className='loading'>加载中...</View>
      </View>
    )
  }

  return (
    <View className='result-page'>
      <View className='status-card'>
        <View className='status-header'>
          <View className='status-icon' style={{ background: getStatusColor(task.status) }}>
            {task.status === 'completed' ? '✓' : task.status === 'failed' ? '✗' : '⟳'}
          </View>
          <View className='status-text'>{getStatusText(task.status)}</View>
        </View>

        {task.status !== 'completed' && task.status !== 'failed' && (
          <View className='progress-container'>
            <View className='progress-bar'>
              <View
                className='progress-fill'
                style={{ width: `${task.progress}%` }}
              />
            </View>
            <View className='progress-text'>{task.progress}%</View>
          </View>
        )}

        {task.error_message && (
          <View className='error-message'>
            <View className='error-icon'>⚠️</View>
            <View className='error-text'>{task.error_message}</View>
          </View>
        )}
      </View>

      {task.status === 'completed' && task.result_url && (
        <View className='result-container'>
          <View className='result-title'>处理结果</View>
          
          <View className='preview-container'>
            {task.result_url.includes('.mp4') || task.result_url.includes('video') ? (
              <Video
                className='video-preview'
                src={task.result_url}
                controls
                showCenterPlayBtn
              />
            ) : (
              <Image
                className='image-preview'
                src={task.result_url}
                mode='aspectFit'
              />
            )}
          </View>

          <View className='action-buttons'>
            <Button className='action-btn primary' onClick={handleCopyUrl}>
              复制链接
            </Button>
            <Button className='action-btn secondary' onClick={handleDownload}>
              下载文件
            </Button>
          </View>
        </View>
      )}

      <View className='bottom-actions'>
        <Button className='back-btn' onClick={handleBackHome}>
          返回首页
        </Button>
      </View>
    </View>
  )
}


