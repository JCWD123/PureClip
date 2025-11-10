import { View, Button, Video, Image } from '@tarojs/components'
import Taro, { useRouter } from '@tarojs/taro'
import { useEffect, useState } from 'react'
import { taskApi } from '../../services/api'
import { API_BASE_URL } from '../../config/api'
import { saveVideoWithAuth, saveImageWithAuth, checkPrivacyAgreement } from '../../utils/saveVideo'
import './index.scss'

export default function Result() {
  const router = useRouter()
  const { taskId } = router.params
  const [task, setTask] = useState<any>(null)
  const [polling, setPolling] = useState(true)
  const [downloading, setDownloading] = useState(false)

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
            title: '视频链接已复制',
            icon: 'success',
            duration: 2000
          })
          // 额外提示：可在浏览器中打开
          setTimeout(() => {
            Taro.showToast({
              title: '可在浏览器中打开下载',
              icon: 'none',
              duration: 2000
            })
          }, 2100)
        },
        fail: () => {
          Taro.showToast({
            title: '复制失败',
            icon: 'error'
          })
        }
      })
    }
  }

  const handleDownload = async () => {
    if (!task?.result_url) {
      Taro.showToast({
        title: '暂无可下载内容',
        icon: 'none'
      })
      return
    }

    if (downloading) {
      return // 防止重复点击
    }

    setDownloading(true)

    try {
      // 判断是视频还是图片
      const isVideo = task.result_url.includes('.mp4') || task.result_url.includes('video')

      // ✅ 步骤1: 检查隐私协议状态（微信2.0隐私协议）
      console.log('🔍 检查隐私协议状态...')
      const needPrivacy = await checkPrivacyAgreement()
      if (needPrivacy) {
        Taro.showModal({
          title: '隐私提示',
          content: '下载功能需要访问您的相册。我们严格遵守微信隐私规范，不会泄露您的个人信息。',
          confirmText: '我知道了',
          showCancel: false
        })
        setDownloading(false)
        return
      }

      Taro.showLoading({
        title: '准备下载...',
        mask: true
      })

      // ✅ 步骤2: 使用后端代理下载（解决域名限制问题）
      const proxyUrl = `${API_BASE_URL}/proxy/download?url=${encodeURIComponent(task.result_url)}`
      
      console.log('📥 使用代理下载:', proxyUrl)

      // 通过代理下载文件到本地临时目录
      const downloadResult = await Taro.downloadFile({
        url: proxyUrl  // ✅ 使用代理URL
      })

      if (downloadResult.statusCode !== 200) {
        throw new Error('下载失败')
      }
      
      console.log('✅ 下载成功，文件路径:', downloadResult.tempFilePath)

      Taro.hideLoading()

      // ✅ 步骤3: 使用授权检测保存到相册（自动处理权限申请）
      if (isVideo) {
        await saveVideoWithAuth(downloadResult.tempFilePath)
      } else {
        await saveImageWithAuth(downloadResult.tempFilePath)
      }

      console.log('🎉 保存成功')
    } catch (error: any) {
      Taro.hideLoading()
      
      console.error('❌ 下载失败:', error)
      
      // 只有在非用户主动取消的情况下才显示错误提示
      if (error !== '用户取消保存' && error !== '用户拒绝授权' && error !== '用户拒绝前往设置') {
        Taro.showToast({
          title: error.errMsg || '下载失败，请稍后重试',
          icon: 'none',
          duration: 2000
        })
      }
    } finally {
      setDownloading(false)
    }
  }

  const handleBackHome = () => {
    Taro.navigateBack()
  }

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      pending: '等待处理',
      downloading: '解析中',
      processing: '获取信息中',
      uploading: '准备完成',
      completed: '解析完成',
      failed: '解析失败'
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
      {/* 处理中状态 */}
      {task.status !== 'completed' && task.status !== 'failed' && (
        <View className='processing-container'>
          <View className='processing-icon'>
            <View className='spinner' />
          </View>
          <View className='processing-title'>{getStatusText(task.status)}</View>
          <View className='progress-container'>
            <View className='progress-bar'>
              <View
                className='progress-fill'
                style={{ width: `${task.progress}%`, background: getStatusColor(task.status) }}
              />
            </View>
            <View className='progress-text'>{task.progress}%</View>
          </View>
          <View className='processing-tip'>请稍候，正在为您处理...</View>
        </View>
      )}

      {/* 失败状态 */}
      {task.status === 'failed' && (
        <View className='error-container'>
          <View className='error-icon-large'>✗</View>
          <View className='error-title'>处理失败</View>
          <View className='error-detail'>{task.error_message || '处理过程中出现错误'}</View>
          <Button className='retry-btn' onClick={handleBackHome}>
            重新尝试
          </Button>
        </View>
      )}

      {/* 成功状态 */}
      {task.status === 'completed' && task.result_url && (
        <View className='success-container'>
          {/* 成功提示 */}
          <View className='success-header'>
            <View className='success-icon'>✓</View>
            <View className='success-title'>处理完成</View>
          </View>

          {/* 视频预览 */}
          <View className='video-section'>
            <View className='section-label'>视频</View>
            <View className='video-wrapper'>
              {task.result_url.includes('.mp4') || task.result_url.includes('video') ? (
                <Video
                  className='video-player'
                  src={task.result_url}
                  controls
                  showCenterPlayBtn
                  objectFit='contain'
                  enableProgressGesture
                  showProgress
                  showPlayBtn
                  showFullscreenBtn
                />
              ) : (
                <Image
                  className='image-preview'
                  src={task.result_url}
                  mode='aspectFit'
                />
              )}
            </View>
          </View>

          {/* 视频信息 */}
          {task.metadata && (
            <View className='info-section'>
              {task.metadata.title && (
                <View className='info-row'>
                  <View className='info-label'>标题：</View>
                  <View className='info-value'>{task.metadata.title}</View>
                </View>
              )}
              {task.metadata.author && (
                <View className='info-row'>
                  <View className='info-label'>作者：</View>
                  <View className='info-value'>{task.metadata.author}</View>
                </View>
              )}
              {task.metadata.platform && (
                <View className='info-row'>
                  <View className='info-label'>平台：</View>
                  <View className='info-value'>{task.metadata.platform}</View>
                </View>
              )}
              {task.metadata.duration && (
                <View className='info-row'>
                  <View className='info-label'>时长：</View>
                  <View className='info-value'>{task.metadata.duration}秒</View>
                </View>
              )}
              {task.metadata.width && task.metadata.height && (
                <View className='info-row'>
                  <View className='info-label'>分辨率：</View>
                  <View className='info-value'>{task.metadata.width}x{task.metadata.height}</View>
                </View>
              )}
            </View>
          )}

          {/* 操作按钮 */}
          <View className='action-section'>
            <Button 
              className='action-btn copy-btn' 
              onClick={handleCopyUrl}
            >
              复制链接
            </Button>
            <Button 
              className='action-btn download-btn' 
              onClick={handleDownload}
              disabled={downloading}
              loading={downloading}
            >
              {downloading ? '保存中...' : '下载视频'}
            </Button>
          </View>

          {/* 底部提示 */}
          <View className='bottom-tip'>
            下载失败？<View className='link-text' onClick={() => {
              Taro.showModal({
                title: '解决方案',
                content: '1. 请确保已授权相册权限\n2. 检查网络连接\n3. 尝试复制链接后在浏览器中打开',
                showCancel: false
              })
            }}>点我查看解决方案</View>
          </View>

          {/* 返回按钮 */}
          <Button className='back-home-btn' onClick={handleBackHome}>
            返回首页
          </Button>
        </View>
      )}
    </View>
  )
}




