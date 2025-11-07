import { createSlice, PayloadAction } from '@reduxjs/toolkit'
import Taro from '@tarojs/taro'

interface UserState {
  userId: string
  hasProfile: boolean
  hasPersona: boolean
  currentPersona: string | null
}

const getUserId = () => {
  try {
    const userId = Taro.getStorageSync('userId')
    if (userId) {
      return userId
    }
  } catch (e) {
    console.error('获取userId失败', e)
  }
  return 'user_' + Date.now()
}

const initialState: UserState = {
  userId: getUserId(),
  hasProfile: false,
  hasPersona: false,
  currentPersona: null,
}

// 保存userId到storage
if (!Taro.getStorageSync('userId')) {
  Taro.setStorageSync('userId', initialState.userId)
}

const userSlice = createSlice({
  name: 'user',
  initialState,
  reducers: {
    setUserId: (state, action: PayloadAction<string>) => {
      state.userId = action.payload
      Taro.setStorageSync('userId', action.payload)
    },
    setHasProfile: (state, action: PayloadAction<boolean>) => {
      state.hasProfile = action.payload
    },
    setHasPersona: (state, action: PayloadAction<boolean>) => {
      state.hasPersona = action.payload
    },
    setCurrentPersona: (state, action: PayloadAction<string | null>) => {
      state.currentPersona = action.payload
    },
  },
})

export const { setUserId, setHasProfile, setHasPersona, setCurrentPersona } = userSlice.actions
export default userSlice.reducer




