import { View, Input, Button, Picker, Textarea } from '@tarojs/components'
import Taro from '@tarojs/taro'
import { useState, useEffect } from 'react'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '../../store'
import { setHasProfile } from '../../store/userSlice'
import { createHealthProfile, getHealthProfile, updateHealthProfile, getPersonaStyles } from '../../services/api'
import './index.scss'

export default function ProfilePage() {
  const [formData, setFormData] = useState({
    nickname: '',
    birth_date: '',
    age: 0,
    gender: '',
    height: 0,
    weight: 0,
    blood_type: '未知',
    lifestyle_habits: '',
    allergies: '',
    medical_history: '',
    adverse_reactions: '',
    family_history: '',
    surgery_history: '',
    vaccination: '',
    other_notes: '',
    persona_style: '',
  })
  const [isEdit, setIsEdit] = useState(false)
  const [personaStyles, setPersonaStyles] = useState<any[]>([])
  const [loadError, setLoadError] = useState<string>('')
  const userId = useSelector((state: RootState) => state.user.userId)
  const dispatch = useDispatch()

  useEffect(() => {
    loadProfile()
    loadPersonaStyles()
  }, [])

  const loadPersonaStyles = async () => {
    try {
      const response: any = await getPersonaStyles()
      if (response.status === 'success') {
        setPersonaStyles(response.data)
      }
    } catch (error) {
      console.error('加载人物风格失败:', error)
    }
  }

  const loadProfile = async () => {
    try {
      setLoadError('')
      const response: any = await getHealthProfile(userId)
      if (response.status === 'success') {
        const data = response.data
        setFormData({
          nickname: data.basic_info?.nickname || '',
          birth_date: data.basic_info?.birth_date || '',
          age: data.basic_info?.age || 0,
          gender: data.basic_info?.gender || '',
          height: data.basic_info?.height || 0,
          weight: data.basic_info?.weight || 0,
          blood_type: data.basic_info?.blood_type || '未知',
          lifestyle_habits: data.health_info?.lifestyle_habits?.join('、') || '',
          allergies: data.health_info?.allergies?.join('、') || '',
          medical_history: data.health_info?.medical_history?.join('、') || '',
          adverse_reactions: data.health_info?.adverse_reactions?.join('、') || '',
          family_history: data.health_info?.family_history?.join('、') || '',
          surgery_history: data.health_info?.surgery_history?.map(s => `${s.name}(${s.date})`).join('、') || '',
          vaccination: data.other_info?.vaccination?.map(v => `${v.name}(${v.date})`).join('、') || '',
          other_notes: data.other_info?.other_notes || '',
          persona_style: data.persona_style || '',
        })
        setIsEdit(true)
        dispatch(setHasProfile(true))
      }
    } catch (error: any) {
      console.log('加载档案错误详情:', {
        message: error.message,
        statusCode: error.statusCode,
        status: error.status,
        error
      })
      
      const statusCode = error.statusCode || error.status
      
      // 404错误表示档案不存在，这是正常的新用户情况，不显示任何错误
      if (statusCode === 404) {
        console.log('用户档案不存在（404），这是正常情况，将显示创建档案界面')
        setLoadError('')
        return
      }
      
      // 401/403 认证错误 - 提示用户登录
      if (statusCode === 401 || statusCode === 403) {
        console.log('认证失败，需要登录')
        setLoadError('authentication')
        return
      }
      
      // 网络错误（没有statusCode）或服务器错误（5xx）
      if (!statusCode || statusCode >= 500) {
        console.log('网络错误或服务器错误')
        setLoadError('network')
        return
      }
      
      // 其他HTTP错误
      console.log('其他错误')
      setLoadError('unknown')
    }
  }

  const handleSubmit = async () => {
    // 验证必填字段
    if (!formData.nickname || !formData.birth_date || !formData.age || !formData.gender || !formData.height || !formData.weight) {
      Taro.showToast({
        title: '请填写完整的基础信息',
        icon: 'none',
        duration: 2000,
      })
      return
    }

    if (!formData.persona_style) {
      Taro.showToast({
        title: '请选择推送人物风格',
        icon: 'none',
        duration: 2000,
      })
      return
    }

    try {
      const profileData = {
        user_id: userId,
        basic_info: {
          nickname: formData.nickname,
          birth_date: formData.birth_date,
          age: formData.age,
          gender: formData.gender,
          height: formData.height,
          weight: formData.weight,
          blood_type: formData.blood_type,
        },
        health_info: {
          lifestyle_habits: formData.lifestyle_habits ? formData.lifestyle_habits.split(/[、,，]/).filter(Boolean) : [],
          allergies: formData.allergies ? formData.allergies.split(/[、,，]/).filter(Boolean) : [],
          medical_history: formData.medical_history ? formData.medical_history.split(/[、,，]/).filter(Boolean) : [],
          adverse_reactions: formData.adverse_reactions ? formData.adverse_reactions.split(/[、,，]/).filter(Boolean) : [],
          family_history: formData.family_history ? formData.family_history.split(/[、,，]/).filter(Boolean) : [],
          surgery_history: [],
        },
        other_info: {
          vaccination: [],
          other_notes: formData.other_notes,
        },
        persona_style: formData.persona_style,
      }

      if (isEdit) {
        await updateHealthProfile(userId, {
          basic_info: profileData.basic_info,
          health_info: profileData.health_info,
          other_info: profileData.other_info,
          persona_style: formData.persona_style,
        })
        Taro.showToast({ title: '健康档案更新成功！', icon: 'success' })
      } else {
        await createHealthProfile(profileData)
        Taro.showToast({ title: '健康档案创建成功！', icon: 'success' })
        setIsEdit(true)
        dispatch(setHasProfile(true))
      }
    } catch (error: any) {
      Taro.showToast({
        title: error.response?.data?.detail || '操作失败，请重试',
        icon: 'none',
      })
    }
  }

  const genderOptions = ['男', '女']
  const bloodTypeOptions = ['A', 'B', 'AB', 'O', '未知']

  return (
    <View className='profile-page'>
      <View className='page-title'>{isEdit ? '编辑健康档案' : '创建健康档案'}</View>

      {loadError === 'authentication' && (
        <View className='error-banner auth-error'>
          <View className='error-icon'>🔐</View>
          <View className='error-content'>
            <View className='error-title'>需要登录</View>
            <View className='error-text'>请先登录或注册账号，才能使用健康档案功能</View>
          </View>
        </View>
      )}

      {loadError === 'network' && (
        <View className='error-banner network-error'>
          <View className='error-icon'>📡</View>
          <View className='error-content'>
            <View className='error-title'>网络连接失败</View>
            <View className='error-text'>无法连接到服务器，请检查网络设置或稍后重试</View>
            <View className='error-retry' onClick={loadProfile}>点击重试</View>
          </View>
        </View>
      )}

      {loadError === 'unknown' && (
        <View className='error-banner unknown-error'>
          <View className='error-icon'>⚠️</View>
          <View className='error-content'>
            <View className='error-title'>加载失败</View>
            <View className='error-text'>加载健康档案时出现问题，请稍后重试</View>
            <View className='error-retry' onClick={loadProfile}>点击重试</View>
          </View>
        </View>
      )}

      <View className='form-section'>
        <View className='section-title'>基础信息</View>

        <View className='form-item'>
          <View className='label'>昵称 *</View>
          <Input
            className='input'
            placeholder='请输入昵称'
            value={formData.nickname}
            onInput={(e) => setFormData({ ...formData, nickname: e.detail.value })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>出生年月 *</View>
          <Input
            className='input'
            placeholder='格式：1990-01'
            value={formData.birth_date}
            onInput={(e) => setFormData({ ...formData, birth_date: e.detail.value })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>年龄 *</View>
          <Input
            className='input'
            type='number'
            placeholder='请输入年龄'
            value={formData.age.toString()}
            onInput={(e) => setFormData({ ...formData, age: parseInt(e.detail.value) || 0 })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>性别 *</View>
          <Picker
            mode='selector'
            range={genderOptions}
            value={genderOptions.indexOf(formData.gender)}
            onChange={(e) => setFormData({ ...formData, gender: genderOptions[e.detail.value] })}
          >
            <View className='picker'>{formData.gender || '请选择性别'}</View>
          </Picker>
        </View>

        <View className='form-item'>
          <View className='label'>身高（cm）*</View>
          <Input
            className='input'
            type='digit'
            placeholder='请输入身高'
            value={formData.height.toString()}
            onInput={(e) => setFormData({ ...formData, height: parseFloat(e.detail.value) || 0 })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>体重（kg）*</View>
          <Input
            className='input'
            type='digit'
            placeholder='请输入体重'
            value={formData.weight.toString()}
            onInput={(e) => setFormData({ ...formData, weight: parseFloat(e.detail.value) || 0 })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>血型</View>
          <Picker
            mode='selector'
            range={bloodTypeOptions}
            value={bloodTypeOptions.indexOf(formData.blood_type)}
            onChange={(e) => setFormData({ ...formData, blood_type: bloodTypeOptions[e.detail.value] })}
          >
            <View className='picker'>{formData.blood_type || '请选择血型'}</View>
          </Picker>
        </View>
      </View>

      <View className='form-section'>
        <View className='section-title'>健康信息</View>
        
        <View className='form-item'>
          <View className='label'>生活习惯</View>
          <View className='hint-small'>常见选项：久坐、熬夜、规律运动、口味偏咸、吸烟、饮酒等</View>
          <Picker
            mode='selector'
            range={['久坐', '熬夜', '规律运动', '规律作息', '口味偏咸', '口味偏辣', '口味偏甜', '吸烟', '饮酒']}
            onChange={(e) => {
              const options = ['久坐', '熬夜', '规律运动', '规律作息', '口味偏咸', '口味偏辣', '口味偏甜', '吸烟', '饮酒']
              const selected = options[e.detail.value]
              const current = formData.lifestyle_habits ? formData.lifestyle_habits + '、' : ''
              setFormData({ ...formData, lifestyle_habits: current + selected })
            }}
          >
            <View className='picker-btn'>点击快速选择 ＋</View>
          </Picker>
          <Input
            className='input'
            placeholder='已选择的内容（可手动编辑，用顿号或逗号分隔）'
            value={formData.lifestyle_habits}
            onInput={(e) => setFormData({ ...formData, lifestyle_habits: e.detail.value })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>过敏史</View>
          <View className='hint-small'>常见过敏原：青霉素、头孢、海鲜、花粉、尘螨、芒果等</View>
          <Picker
            mode='selector'
            range={['青霉素', '头孢', '鸡蛋', '牛奶', '海鲜', '花粉', '尘螨', '芒果', '坚果']}
            onChange={(e) => {
              const options = ['青霉素', '头孢', '鸡蛋', '牛奶', '海鲜', '花粉', '尘螨', '芒果', '坚果']
              const selected = options[e.detail.value]
              const current = formData.allergies ? formData.allergies + '、' : ''
              setFormData({ ...formData, allergies: current + selected })
            }}
          >
            <View className='picker-btn'>点击快速选择 ＋</View>
          </Picker>
          <Input
            className='input'
            placeholder='已选择的内容（可手动编辑，用顿号或逗号分隔）'
            value={formData.allergies}
            onInput={(e) => setFormData({ ...formData, allergies: e.detail.value })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>既往病史</View>
          <View className='hint-small'>常见疾病：高血压、糖尿病、高血脂、心脏病、哮喘、胃病等</View>
          <Picker
            mode='selector'
            range={['高血压', '糖尿病', '高血脂', '心脏病', '哮喘', '乙肝', '胃病', '关节炎']}
            onChange={(e) => {
              const options = ['高血压', '糖尿病', '高血脂', '心脏病', '哮喘', '乙肝', '胃病', '关节炎']
              const selected = options[e.detail.value]
              const current = formData.medical_history ? formData.medical_history + '、' : ''
              setFormData({ ...formData, medical_history: current + selected })
            }}
          >
            <View className='picker-btn'>点击快速选择 ＋</View>
          </Picker>
          <Input
            className='input'
            placeholder='已选择的内容（可手动编辑，用顿号或逗号分隔）'
            value={formData.medical_history}
            onInput={(e) => setFormData({ ...formData, medical_history: e.detail.value })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>药品不良反应</View>
          <View className='hint-small'>记录对药物的不良反应，如皮疹、呼吸困难等</View>
          <Input
            className='input'
            placeholder='例如：阿司匹林过敏（用顿号或逗号分隔）'
            value={formData.adverse_reactions}
            onInput={(e) => setFormData({ ...formData, adverse_reactions: e.detail.value })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>家族史</View>
          <View className='hint-small'>记录家族中有的疾病，如遗传性疾病、肿瘤等</View>
          <Input
            className='input'
            placeholder='例如：高血压、心脏病（用顿号或逗号分隔）'
            value={formData.family_history}
            onInput={(e) => setFormData({ ...formData, family_history: e.detail.value })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>手术史</View>
          <View className='hint-small'>记录既往手术经历及时间</View>
          <Input
            className='input'
            placeholder='例如：阑尾切除(2020-01)（用顿号或逗号分隔）'
            value={formData.surgery_history}
            onInput={(e) => setFormData({ ...formData, surgery_history: e.detail.value })}
          />
        </View>
      </View>

      <View className='form-section'>
        <View className='section-title'>其他信息</View>
        
        <View className='form-item'>
          <View className='label'>疫苗接种记录</View>
          <View className='hint-small'>记录疫苗接种情况及时间，如：新冠疫苗、流感疫苗等</View>
          <Input
            className='input'
            placeholder='例如：新冠疫苗(2023-01)（用顿号或逗号分隔）'
            value={formData.vaccination}
            onInput={(e) => setFormData({ ...formData, vaccination: e.detail.value })}
          />
        </View>

        <View className='form-item'>
          <View className='label'>其他备注</View>
          <View className='hint-small'>可包含以下信息：</View>
          <View className='hint-small'>• 特殊体质（如过敏体质、寒性体质等）</View>
          <View className='hint-small'>• 长期服用的药物或保健品</View>
          <View className='hint-small'>• 运动习惯和频率</View>
          <View className='hint-small'>• 睡眠质量和作息时间</View>
          <View className='hint-small'>• 饮食偏好和禁忌</View>
          <View className='hint-small'>• 心理健康状况</View>
          <View className='hint-small'>• 其他需要医生了解的健康信息</View>
          <Textarea
            className='textarea'
            placeholder='请详细描述...'
            value={formData.other_notes}
            onInput={(e) => setFormData({ ...formData, other_notes: e.detail.value })}
          />
        </View>
      </View>

      <View className='form-section'>
        <View className='section-title'>🎭 推送人物风格</View>
        <View className='hint-small' style='margin-bottom: 20px;'>选择您喜欢的推送风格，让健康资讯更有温度（必选）</View>
        
        <View className='persona-styles-list'>
          {personaStyles.map((style, index) => (
            <View
              key={index}
              className={`persona-style-item ${formData.persona_style === style.style_name ? 'active' : ''}`}
              onClick={() => setFormData({ ...formData, persona_style: style.style_name })}
            >
              <View className='persona-icon'>{style.icon}</View>
              <View className='persona-content'>
                <View className='persona-name'>{style.style_name}</View>
                <View className='persona-desc'>{style.description}</View>
              </View>
              {formData.persona_style === style.style_name && (
                <View className='persona-check'>✓</View>
              )}
            </View>
          ))}
        </View>
      </View>

      <View className='submit-button'>
        <Button type='primary' onClick={handleSubmit}>
          {isEdit ? '更新档案' : '创建档案'}
        </Button>
      </View>
    </View>
  )
}



