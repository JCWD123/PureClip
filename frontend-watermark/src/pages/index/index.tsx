import { View, Input, Button, Picker } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useState } from 'react'
import { useDispatch } from 'react-redux'
import { setCurrentTask } from '../../store/taskSlice'
import { taskApi } from '../../services/api'
import './index.scss'

export default function Index() {
  const dispatch = useDispatch()
  const [url, setUrl] = useState('')
  const [mediaType, setMediaType] = useState<'video' | 'image'>('video')
  const [method, setMethod] = useState<'crop' | 'blur' | 'cover' | 'inpaint'>('crop')
  const [loading, setLoading] = useState(false)

  const mediaTypeOptions = [
    { label: '视频', value: 'video' },
    { label: '图片', value: 'image' }
  ]

  const methodOptions = [
    { label: '裁剪（最快）', value: 'crop' },
    { label: '模糊处理', value: 'blur' },
    { label: '覆盖处理', value: 'cover' },
    { label: '智能填充', value: 'inpaint' }
  ]

  const [mediaTypeIndex, setMediaTypeIndex] = useState(0)
  const [methodIndex, setMethodIndex] = useState(0)

  const handleMediaTypeChange = (e: any) => {
    const index = e.detail.value
    setMediaTypeIndex(index)
    setMediaType(mediaTypeOptions[index].value as 'video' | 'image')
  }

  const handleMethodChange = (e: any) => {
    const index = e.detail.value
    setMethodIndex(index)
    setMethod(methodOptions[index].value as any)
  }

  const handleSubmit = async () => {
    if (!url) {
      Taro.showToast({
        title: '请输入视频或图片URL',
        icon: 'none'
      })
      return
    }

    try {
      setLoading(true)

      // 创建任务
      const result = await taskApi.createTask({
        url,
        media_type: mediaType,
        method,
        user_id: 'test_user_001' // 这里应该从用户系统获取
      })

      dispatch(setCurrentTask(result))

      Taro.showToast({
        title: '任务创建成功',
        icon: 'success'
      })

      // 跳转到结果页面
      setTimeout(() => {
        Taro.navigateTo({
          url: `/pages/result/index?taskId=${result.task_id}`
        })
      }, 1000)

    } catch (error: any) {
      console.error('创建任务失败:', error)
      Taro.showToast({
        title: error.message || '创建任务失败',
        icon: 'none'
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <View className='index-page'>
      <View className='header'>
        <View className='title'>PureClip 去水印</View>
        <View className='subtitle'>快速去除视频和图片水印</View>
      </View>

      <View className='form-container'>
        <View className='form-item'>
          <View className='form-label'>媒体类型</View>
          <Picker
            mode='selector'
            range={mediaTypeOptions.map(o => o.label)}
            value={mediaTypeIndex}
            onChange={handleMediaTypeChange}
          >
            <View className='picker'>
              {mediaTypeOptions[mediaTypeIndex].label}
            </View>
          </Picker>
        </View>

        <View className='form-item'>
          <View className='form-label'>去水印方法</View>
          <Picker
            mode='selector'
            range={methodOptions.map(o => o.label)}
            value={methodIndex}
            onChange={handleMethodChange}
          >
            <View className='picker'>
              {methodOptions[methodIndex].label}
            </View>
          </Picker>
        </View>

        <View className='form-item'>
          <View className='form-label'>视频/图片链接</View>
          <Input
            className='input'
            type='text'
            placeholder='请输入视频或图片URL'
            value={url}
            onInput={(e) => setUrl(e.detail.value)}
          />
        </View>

        <View className='method-tips'>
          <View className='tips-title'>💡 去水印方法说明：</View>
          <View className='tips-item'>• 裁剪：直接裁掉水印区域（速度最快）</View>
          <View className='tips-item'>• 模糊：对水印区域进行模糊处理</View>
          <View className='tips-item'>• 覆盖：用周围颜色覆盖水印</View>
          <View className='tips-item'>• 智能填充：AI智能修复水印区域</View>
        </View>

        <Button
          className='submit-btn'
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? '处理中...' : '开始处理'}
        </Button>
      </View>

      <View className='features'>
        <View className='feature-item'>
          <View className='feature-icon'>⚡️</View>
          <View className='feature-text'>快速处理</View>
        </View>
        <View className='feature-item'>
          <View className='feature-icon'>🎯</View>
          <View className='feature-text'>高质量</View>
        </View>
        <View className='feature-item'>
          <View className='feature-icon'>🔒</View>
          <View className='feature-text'>安全可靠</View>
        </View>
      </View>
    </View>
  )
}


