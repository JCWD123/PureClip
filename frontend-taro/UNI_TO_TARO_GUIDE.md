# 从 uni-app 到 Taro React 开发完整指南

> 本指南专为有 uni-app 开发经验的开发者设计，帮助您快速掌握 Taro + React 多端开发。

---

## 📚 目录

1. [框架对比概览](#1-框架对比概览)
2. [核心概念对照](#2-核心概念对照)
3. [项目结构对比](#3-项目结构对比)
4. [生命周期对比](#4-生命周期对比)
5. [组件系统对比](#5-组件系统对比)
6. [路由导航对比](#6-路由导航对比)
7. [状态管理对比](#7-状态管理对比)
8. [网络请求对比](#8-网络请求对比)
9. [样式处理对比](#9-样式处理对比)
10. [常用API对比](#10-常用api对比)
11. [实战案例对比](#11-实战案例对比)
12. [最佳实践](#12-最佳实践)
13. [踩坑指南](#13-踩坑指南)

---

## 1. 框架对比概览

### 1.1 核心差异

| 维度 | uni-app | Taro React |
|------|---------|------------|
| **语法** | Vue 2/3 | React |
| **编译器** | uni-compiler | Taro CLI |
| **组件库** | uni-ui | Taro Components + taro-ui |
| **状态管理** | Vuex / Pinia | Redux / MobX / Context |
| **数据绑定** | 模板语法（双向绑定） | JSX（单向数据流） |
| **生命周期** | Vue 生命周期 | React Hooks |
| **样式** | rpx | rpx（自动转换） |
| **TypeScript** | 支持 | 强力推荐 |
| **多端支持** | ✅ 全平台 | ✅ 全平台 |

### 1.2 为什么选择 Taro React？

**优势：**
- ✅ React 生态更庞大（npm包更丰富）
- ✅ TypeScript 支持更完善
- ✅ 适合大型项目和团队协作
- ✅ Hooks 让逻辑复用更简单
- ✅ 性能优化工具更多（React DevTools）
- ✅ 社区活跃度高

**劣势：**
- ❌ 学习曲线稍陡（需要理解Hooks、JSX）
- ❌ 需要手动管理状态（不如Vue双向绑定方便）

---

## 2. 核心概念对照

### 2.1 数据绑定

**uni-app (Vue):**
```vue
<template>
  <view>
    <text>{{ message }}</text>
    <input v-model="message" />
  </view>
</template>

<script>
export default {
  data() {
    return {
      message: 'Hello'
    }
  }
}
</script>
```

**Taro React:**
```tsx
import { View, Text, Input } from '@tarojs/components'
import { useState } from 'react'

export default function Page() {
  const [message, setMessage] = useState('Hello')

  return (
    <View>
      <Text>{message}</Text>
      <Input 
        value={message} 
        onInput={(e) => setMessage(e.detail.value)} 
      />
    </View>
  )
}
```

**关键差异：**
- ❌ Taro **没有** `v-model` 双向绑定
- ✅ 需要手动处理 `value` 和 `onInput` 事件
- ✅ 使用 `useState` Hook 管理状态

---

### 2.2 条件渲染

**uni-app (Vue):**
```vue
<template>
  <view v-if="show">显示内容</view>
  <view v-else>隐藏内容</view>
</template>
```

**Taro React:**
```tsx
<View>
  {show ? <View>显示内容</View> : <View>隐藏内容</View>}
</View>

// 或者使用逻辑与运算符
<View>
  {show && <View>显示内容</View>}
</View>
```

---

### 2.3 列表渲染

**uni-app (Vue):**
```vue
<template>
  <view v-for="(item, index) in list" :key="item.id">
    {{ item.name }}
  </view>
</template>
```

**Taro React:**
```tsx
<View>
  {list.map((item, index) => (
    <View key={item.id}>
      {item.name}
    </View>
  ))}
</View>
```

---

### 2.4 事件处理

**uni-app (Vue):**
```vue
<template>
  <button @click="handleClick">点击</button>
  <button @click="handleWithParam(123)">带参数</button>
</template>

<script>
export default {
  methods: {
    handleClick() {
      console.log('点击了')
    },
    handleWithParam(id) {
      console.log('ID:', id)
    }
  }
}
</script>
```

**Taro React:**
```tsx
import { Button } from '@tarojs/components'

export default function Page() {
  const handleClick = () => {
    console.log('点击了')
  }

  const handleWithParam = (id: number) => {
    console.log('ID:', id)
  }

  return (
    <View>
      <Button onClick={handleClick}>点击</Button>
      <Button onClick={() => handleWithParam(123)}>带参数</Button>
    </View>
  )
}
```

---

## 3. 项目结构对比

### 3.1 uni-app 项目结构

```
uni-app-project/
├── pages/                # 页面
│   ├── index/
│   │   ├── index.vue
│   │   └── index.json    # 页面配置
├── components/           # 组件
├── static/               # 静态资源
├── store/                # Vuex
├── App.vue               # 应用入口
├── main.js               # 主入口
├── manifest.json         # 应用配置
└── pages.json            # 页面路由配置
```

### 3.2 Taro React 项目结构

```
taro-project/
├── src/
│   ├── pages/            # 页面
│   │   ├── index/
│   │   │   ├── index.tsx
│   │   │   ├── index.scss
│   │   │   └── index.config.ts  # 页面配置
│   ├── components/       # 组件
│   ├── assets/           # 静态资源
│   ├── store/            # Redux
│   ├── services/         # API服务
│   ├── utils/            # 工具函数
│   ├── app.tsx           # 应用入口
│   ├── app.config.ts     # 应用配置（类似pages.json）
│   └── app.scss
├── config/               # Taro配置
│   ├── index.ts
│   ├── dev.ts
│   └── prod.ts
├── project.config.json   # 微信小程序配置
└── package.json
```

**关键差异：**
- ❌ Taro **没有** `pages.json`，路由配置在 `app.config.ts`
- ✅ 每个页面有独立的 `.config.ts` 文件
- ✅ 配置文件使用 TypeScript

---

## 4. 生命周期对比

### 4.1 页面生命周期

**uni-app (Vue):**
```vue
<script>
export default {
  onLoad(options) {
    // 页面加载（类似created）
    console.log('页面加载', options)
  },
  onShow() {
    // 页面显示
  },
  onReady() {
    // 页面初次渲染完成
  },
  onHide() {
    // 页面隐藏
  },
  onUnload() {
    // 页面卸载
  },
  onPullDownRefresh() {
    // 下拉刷新
  },
  onReachBottom() {
    // 上拉触底
  }
}
</script>
```

**Taro React:**
```tsx
import Taro, { useLoad, useDidShow, useReady, useDidHide, useUnload, usePullDownRefresh, useReachBottom } from '@tarojs/taro'
import { useEffect } from 'react'

export default function Page() {
  // 页面加载（获取路由参数）
  useLoad((options) => {
    console.log('页面加载', options)
  })

  // 页面显示
  useDidShow(() => {
    console.log('页面显示')
  })

  // 页面初次渲染完成
  useReady(() => {
    console.log('页面渲染完成')
  })

  // 页面隐藏
  useDidHide(() => {
    console.log('页面隐藏')
  })

  // 页面卸载
  useUnload(() => {
    console.log('页面卸载')
  })

  // 下拉刷新
  usePullDownRefresh(() => {
    console.log('下拉刷新')
    // 停止下拉刷新
    Taro.stopPullDownRefresh()
  })

  // 上拉触底
  useReachBottom(() => {
    console.log('上拉触底')
  })

  // 相当于 Vue 的 mounted（仅执行一次）
  useEffect(() => {
    console.log('组件挂载')
    return () => {
      console.log('组件卸载')
    }
  }, [])

  return <View>页面内容</View>
}
```

### 4.2 应用生命周期

**uni-app (Vue):**
```javascript
// App.vue
export default {
  onLaunch(options) {
    console.log('App Launch', options)
  },
  onShow(options) {
    console.log('App Show', options)
  },
  onHide() {
    console.log('App Hide')
  }
}
```

**Taro React:**
```tsx
// app.tsx
import { useLaunch, useDidShow, useDidHide } from '@tarojs/taro'

function App({ children }) {
  useLaunch((options) => {
    console.log('App Launch', options)
  })

  useDidShow((options) => {
    console.log('App Show', options)
  })

  useDidHide(() => {
    console.log('App Hide')
  })

  return children
}

export default App
```

---

## 5. 组件系统对比

### 5.1 基础组件

**uni-app (Vue):**
```vue
<template>
  <view class="container">
    <text>文本</text>
    <image src="/static/logo.png" />
    <button @click="handleClick">按钮</button>
    <input v-model="value" placeholder="输入框" />
    <scroll-view scroll-y>
      <view>滚动内容</view>
    </scroll-view>
  </view>
</template>
```

**Taro React:**
```tsx
import { View, Text, Image, Button, Input, ScrollView } from '@tarojs/components'

export default function Page() {
  const [value, setValue] = useState('')

  return (
    <View className='container'>
      <Text>文本</Text>
      <Image src='/static/logo.png' />
      <Button onClick={handleClick}>按钮</Button>
      <Input 
        value={value}
        onInput={(e) => setValue(e.detail.value)}
        placeholder='输入框'
      />
      <ScrollView scrollY>
        <View>滚动内容</View>
      </ScrollView>
    </View>
  )
}
```

**关键差异：**
- ✅ 组件名称基本一致，但需要从 `@tarojs/components` 导入
- ✅ 事件名采用驼峰命名：`@click` → `onClick`
- ✅ 属性名采用驼峰命名：`scroll-y` → `scrollY`

### 5.2 自定义组件

**uni-app (Vue):**
```vue
<!-- components/MyButton.vue -->
<template>
  <button @click="handleClick">
    {{ text }}
  </button>
</template>

<script>
export default {
  props: {
    text: {
      type: String,
      default: '按钮'
    }
  },
  methods: {
    handleClick() {
      this.$emit('click')
    }
  }
}
</script>

<!-- 使用 -->
<template>
  <my-button text="点击我" @click="onButtonClick" />
</template>
```

**Taro React:**
```tsx
// components/MyButton.tsx
import { Button } from '@tarojs/components'

interface Props {
  text?: string
  onClick?: () => void
}

export default function MyButton({ text = '按钮', onClick }: Props) {
  return (
    <Button onClick={onClick}>
      {text}
    </Button>
  )
}

// 使用
import MyButton from '@/components/MyButton'

<MyButton text='点击我' onClick={onButtonClick} />
```

---

## 6. 路由导航对比

### 6.1 路由配置

**uni-app (Vue):**
```json
// pages.json
{
  "pages": [
    {
      "path": "pages/index/index",
      "style": {
        "navigationBarTitleText": "首页"
      }
    },
    {
      "path": "pages/detail/detail",
      "style": {
        "navigationBarTitleText": "详情"
      }
    }
  ],
  "tabBar": {
    "list": [
      {
        "pagePath": "pages/index/index",
        "text": "首页",
        "iconPath": "static/home.png",
        "selectedIconPath": "static/home-active.png"
      }
    ]
  }
}
```

**Taro React:**
```typescript
// app.config.ts
export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/detail/index'
  ],
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#fff',
    navigationBarTitleText: 'WeChat',
    navigationBarTextStyle: 'black'
  },
  tabBar: {
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页',
        iconPath: 'assets/home.png',
        selectedIconPath: 'assets/home-active.png'
      }
    ]
  }
})
```

```typescript
// pages/index/index.config.ts
export default definePageConfig({
  navigationBarTitleText: '首页'
})
```

### 6.2 页面跳转

**uni-app (Vue):**
```javascript
// 保留当前页面，跳转到应用内的某个页面
uni.navigateTo({
  url: '/pages/detail/detail?id=123'
})

// 关闭当前页面，跳转到应用内的某个页面
uni.redirectTo({
  url: '/pages/detail/detail?id=123'
})

// 跳转到 tabBar 页面
uni.switchTab({
  url: '/pages/index/index'
})

// 关闭所有页面，打开到应用内的某个页面
uni.reLaunch({
  url: '/pages/index/index'
})

// 返回上一页
uni.navigateBack({
  delta: 1
})
```

**Taro React:**
```typescript
import Taro from '@tarojs/taro'

// 保留当前页面，跳转到应用内的某个页面
Taro.navigateTo({
  url: '/pages/detail/index?id=123'
})

// 关闭当前页面，跳转到应用内的某个页面
Taro.redirectTo({
  url: '/pages/detail/index?id=123'
})

// 跳转到 tabBar 页面
Taro.switchTab({
  url: '/pages/index/index'
})

// 关闭所有页面，打开到应用内的某个页面
Taro.reLaunch({
  url: '/pages/index/index'
})

// 返回上一页
Taro.navigateBack({
  delta: 1
})
```

### 6.3 接收路由参数

**uni-app (Vue):**
```javascript
export default {
  onLoad(options) {
    console.log(options.id)  // 123
  }
}
```

**Taro React:**
```tsx
import { useLoad } from '@tarojs/taro'

export default function DetailPage() {
  useLoad((options) => {
    console.log(options.id)  // 123
  })
}

// 或使用 Taro.getCurrentInstance()
import Taro from '@tarojs/taro'
import { useEffect } from 'react'

export default function DetailPage() {
  useEffect(() => {
    const { id } = Taro.getCurrentInstance().router.params
    console.log(id)  // 123
  }, [])
}
```

---

## 7. 状态管理对比

### 7.1 全局状态管理

**uni-app (Vuex):**
```javascript
// store/index.js
import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    count: 0
  },
  mutations: {
    increment(state) {
      state.count++
    }
  },
  actions: {
    incrementAsync({ commit }) {
      setTimeout(() => {
        commit('increment')
      }, 1000)
    }
  }
})

// 使用
<template>
  <view>
    <text>{{ count }}</text>
    <button @click="increment">增加</button>
  </view>
</template>

<script>
import { mapState, mapMutations } from 'vuex'

export default {
  computed: {
    ...mapState(['count'])
  },
  methods: {
    ...mapMutations(['increment'])
  }
}
</script>
```

**Taro React (Redux Toolkit):**
```typescript
// store/index.ts
import { configureStore } from '@reduxjs/toolkit'
import counterReducer from './counterSlice'

export const store = configureStore({
  reducer: {
    counter: counterReducer
  }
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch

// store/counterSlice.ts
import { createSlice } from '@reduxjs/toolkit'

interface CounterState {
  count: number
}

const initialState: CounterState = {
  count: 0
}

const counterSlice = createSlice({
  name: 'counter',
  initialState,
  reducers: {
    increment: (state) => {
      state.count += 1
    }
  }
})

export const { increment } = counterSlice.actions
export default counterSlice.reducer

// 使用
import { View, Text, Button } from '@tarojs/components'
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '@/store'
import { increment } from '@/store/counterSlice'

export default function Page() {
  const count = useSelector((state: RootState) => state.counter.count)
  const dispatch = useDispatch()

  return (
    <View>
      <Text>{count}</Text>
      <Button onClick={() => dispatch(increment())}>增加</Button>
    </View>
  )
}
```

### 7.2 本地存储

**uni-app:**
```javascript
// 设置
uni.setStorageSync('key', 'value')

// 获取
const value = uni.getStorageSync('key')

// 删除
uni.removeStorageSync('key')

// 清空
uni.clearStorageSync()
```

**Taro React:**
```typescript
import Taro from '@tarojs/taro'

// 设置
Taro.setStorageSync('key', 'value')

// 获取
const value = Taro.getStorageSync('key')

// 删除
Taro.removeStorageSync('key')

// 清空
Taro.clearStorageSync()
```

---

## 8. 网络请求对比

### 8.1 基础请求

**uni-app (Vue):**
```javascript
uni.request({
  url: 'https://api.example.com/data',
  method: 'POST',
  data: {
    name: 'test'
  },
  success: (res) => {
    console.log(res.data)
  },
  fail: (err) => {
    console.error(err)
  }
})
```

**Taro React:**
```typescript
import Taro from '@tarojs/taro'

Taro.request({
  url: 'https://api.example.com/data',
  method: 'POST',
  data: {
    name: 'test'
  }
}).then(res => {
  console.log(res.data)
}).catch(err => {
  console.error(err)
})
```

### 8.2 封装请求工具

**uni-app (Vue):**
```javascript
// utils/request.js
export function request(options) {
  return new Promise((resolve, reject) => {
    uni.showLoading({ title: '加载中...' })
    
    uni.request({
      ...options,
      success: (res) => {
        uni.hideLoading()
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(res)
        }
      },
      fail: (err) => {
        uni.hideLoading()
        uni.showToast({ title: '请求失败', icon: 'none' })
        reject(err)
      }
    })
  })
}

// 使用
import { request } from '@/utils/request'

request({
  url: '/api/data',
  method: 'GET'
}).then(data => {
  console.log(data)
})
```

**Taro React:**
```typescript
// utils/request.ts
import Taro from '@tarojs/taro'

const API_BASE_URL = 'https://api.example.com'

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE'
  data?: any
  header?: any
}

export const request = async (url: string, options: RequestOptions = {}) => {
  const { method = 'GET', data, header = {} } = options

  try {
    Taro.showLoading({ title: '加载中...' })

    const response = await Taro.request({
      url: `${API_BASE_URL}${url}`,
      method,
      data,
      header: {
        'Content-Type': 'application/json',
        ...header
      }
    })

    Taro.hideLoading()

    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response.data
    } else {
      throw new Error(`请求失败: ${response.statusCode}`)
    }
  } catch (error) {
    Taro.hideLoading()
    Taro.showToast({ title: '网络请求失败', icon: 'none' })
    throw error
  }
}

// 使用
import { request } from '@/utils/request'

const data = await request('/api/data', { method: 'GET' })
```

---

## 9. 样式处理对比

### 9.1 样式单位

**两者都支持 rpx（响应式像素）：**
- 750rpx = 屏幕宽度
- 1rpx = 屏幕宽度 / 750

### 9.2 样式写法

**uni-app (Vue):**
```vue
<template>
  <view class="container">
    <text :class="{ active: isActive }">文本</text>
    <view :style="{ color: textColor }">动态样式</view>
  </view>
</template>

<style scoped lang="scss">
.container {
  padding: 30rpx;

  .active {
    color: red;
  }
}
</style>
```

**Taro React:**
```tsx
import { View, Text } from '@tarojs/components'
import './index.scss'

export default function Page() {
  const isActive = true
  const textColor = 'red'

  return (
    <View className='container'>
      <Text className={isActive ? 'active' : ''}>文本</Text>
      <View style={{ color: textColor }}>动态样式</View>
    </View>
  )
}
```

```scss
// index.scss
.container {
  padding: 30px;

  .active {
    color: red;
  }
}
```

---

## 10. 常用API对比

### 10.1 界面交互

| 功能 | uni-app | Taro React |
|------|---------|------------|
| 提示框 | `uni.showToast()` | `Taro.showToast()` |
| 加载中 | `uni.showLoading()` | `Taro.showLoading()` |
| 模态框 | `uni.showModal()` | `Taro.showModal()` |
| 操作菜单 | `uni.showActionSheet()` | `Taro.showActionSheet()` |

```typescript
// 示例
Taro.showToast({
  title: '成功',
  icon: 'success',
  duration: 2000
})

Taro.showModal({
  title: '提示',
  content: '确认删除吗？',
  success: (res) => {
    if (res.confirm) {
      console.log('用户点击确定')
    }
  }
})
```

### 10.2 界面导航栏

| 功能 | uni-app | Taro React |
|------|---------|------------|
| 设置标题 | `uni.setNavigationBarTitle()` | `Taro.setNavigationBarTitle()` |
| 显示加载 | `uni.showNavigationBarLoading()` | `Taro.showNavigationBarLoading()` |
| 隐藏加载 | `uni.hideNavigationBarLoading()` | `Taro.hideNavigationBarLoading()` |

### 10.3 文件操作

| 功能 | uni-app | Taro React |
|------|---------|------------|
| 选择图片 | `uni.chooseImage()` | `Taro.chooseImage()` |
| 预览图片 | `uni.previewImage()` | `Taro.previewImage()` |
| 上传文件 | `uni.uploadFile()` | `Taro.uploadFile()` |
| 下载文件 | `uni.downloadFile()` | `Taro.downloadFile()` |

---

## 11. 实战案例对比

### 案例：用户列表页面（含下拉刷新、上拉加载）

**uni-app (Vue):**
```vue
<template>
  <view class="container">
    <view v-for="item in list" :key="item.id" class="item">
      <text>{{ item.name }}</text>
    </view>
    <view v-if="loading" class="loading">加载中...</view>
  </view>
</template>

<script>
export default {
  data() {
    return {
      list: [],
      page: 1,
      loading: false
    }
  },
  onLoad() {
    this.loadData()
  },
  onPullDownRefresh() {
    this.page = 1
    this.list = []
    this.loadData().then(() => {
      uni.stopPullDownRefresh()
    })
  },
  onReachBottom() {
    this.loadMore()
  },
  methods: {
    async loadData() {
      this.loading = true
      const res = await uni.request({
        url: `/api/users?page=${this.page}`
      })
      this.list = res.data.data
      this.loading = false
    },
    async loadMore() {
      if (this.loading) return
      this.page++
      this.loading = true
      const res = await uni.request({
        url: `/api/users?page=${this.page}`
      })
      this.list = [...this.list, ...res.data.data]
      this.loading = false
    }
  }
}
</script>

<style scoped lang="scss">
.container {
  padding: 30rpx;
}
.item {
  padding: 20rpx;
  margin-bottom: 20rpx;
  background: #fff;
  border-radius: 10rpx;
}
</style>
```

**Taro React:**
```tsx
import { View, Text } from '@tarojs/components'
import Taro, { useLoad, usePullDownRefresh, useReachBottom } from '@tarojs/taro'
import { useState } from 'react'
import { request } from '@/utils/request'
import './index.scss'

interface User {
  id: number
  name: string
}

export default function UserListPage() {
  const [list, setList] = useState<User[]>([])
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(false)

  useLoad(() => {
    loadData(1)
  })

  usePullDownRefresh(() => {
    setPage(1)
    setList([])
    loadData(1).then(() => {
      Taro.stopPullDownRefresh()
    })
  })

  useReachBottom(() => {
    loadMore()
  })

  const loadData = async (pageNum: number) => {
    setLoading(true)
    try {
      const res: any = await request(`/api/users?page=${pageNum}`)
      setList(res.data)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  const loadMore = async () => {
    if (loading) return
    const nextPage = page + 1
    setPage(nextPage)
    setLoading(true)
    try {
      const res: any = await request(`/api/users?page=${nextPage}`)
      setList([...list, ...res.data])
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <View className='container'>
      {list.map(item => (
        <View key={item.id} className='item'>
          <Text>{item.name}</Text>
        </View>
      ))}
      {loading && <View className='loading'>加载中...</View>}
    </View>
  )
}
```

```scss
// index.scss
.container {
  padding: 30px;
}
.item {
  padding: 20px;
  margin-bottom: 20px;
  background: #fff;
  border-radius: 10px;
}
```

```typescript
// index.config.ts
export default definePageConfig({
  navigationBarTitleText: '用户列表',
  enablePullDownRefresh: true  // 开启下拉刷新
})
```

---

## 12. 最佳实践

### 12.1 TypeScript 类型定义

```typescript
// types/user.ts
export interface User {
  id: number
  name: string
  avatar?: string
  age: number
}

// 在页面中使用
import { User } from '@/types/user'

const [user, setUser] = useState<User | null>(null)
```

### 12.2 自定义 Hooks 复用逻辑

**uni-app (Vue):**
```javascript
// mixins/loadData.js
export default {
  data() {
    return {
      list: [],
      loading: false
    }
  },
  methods: {
    async loadData() {
      this.loading = true
      // ...
    }
  }
}

// 使用
import loadDataMixin from '@/mixins/loadData'
export default {
  mixins: [loadDataMixin]
}
```

**Taro React (Custom Hook):**
```typescript
// hooks/useLoadData.ts
import { useState } from 'react'
import { request } from '@/utils/request'

export function useLoadData<T>(url: string) {
  const [list, setList] = useState<T[]>([])
  const [loading, setLoading] = useState(false)

  const loadData = async () => {
    setLoading(true)
    try {
      const res: any = await request(url)
      setList(res.data)
    } catch (error) {
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return { list, loading, loadData, setList }
}

// 使用
import { useLoadData } from '@/hooks/useLoadData'
import { User } from '@/types/user'

export default function Page() {
  const { list, loading, loadData } = useLoadData<User>('/api/users')

  useLoad(() => {
    loadData()
  })

  return (
    // ...
  )
}
```

### 12.3 环境变量配置

**uni-app:**
```javascript
// 在 manifest.json 中配置不同环境的 API_URL
const API_URL = process.env.VUE_APP_API_URL || 'https://api.example.com'
```

**Taro React:**
```typescript
// config/index.ts
export default {
  defineConstants: {
    TARO_APP_API_URL: JSON.stringify(process.env.TARO_APP_API_URL || 'https://api.medai.medai-zjgsu.cn')
  }
}

// 使用
const API_BASE_URL = process.env.TARO_APP_API_URL || 'https://api.medai.medai-zjgsu.cn'
```

---

## 13. 踩坑指南

### 13.1 常见错误

❌ **错误 1：直接修改 state**
```tsx
// 错误写法
const [user, setUser] = useState({ name: 'Tom' })
user.name = 'Jerry'  // ❌ 不会触发更新

// 正确写法
setUser({ ...user, name: 'Jerry' })  // ✅
```

❌ **错误 2：useEffect 无限循环**
```tsx
// 错误写法
useEffect(() => {
  loadData()  // ❌ 如果 loadData 改变了 state，会无限循环
})

// 正确写法
useEffect(() => {
  loadData()
}, [])  // ✅ 空数组表示仅在组件挂载时执行一次
```

❌ **错误 3：事件处理函数写法错误**
```tsx
// 错误写法
<Button onClick={handleClick()}>点击</Button>  // ❌ 会立即执行

// 正确写法
<Button onClick={handleClick}>点击</Button>  // ✅
<Button onClick={() => handleClick(123)}>点击</Button>  // ✅ 带参数
```

### 13.2 性能优化

**1. 使用 useMemo 缓存计算结果**
```tsx
import { useMemo } from 'react'

const expensiveValue = useMemo(() => {
  return computeExpensiveValue(a, b)
}, [a, b])  // 仅当 a 或 b 变化时重新计算
```

**2. 使用 useCallback 缓存函数**
```tsx
import { useCallback } from 'react'

const handleClick = useCallback(() => {
  // 处理逻辑
}, [])  // 函数不会在每次渲染时重新创建
```

**3. 列表渲染优化**
```tsx
// 使用 key 优化列表渲染
{list.map(item => (
  <View key={item.id}>  {/* ✅ 使用唯一ID作为key */}
    {item.name}
  </View>
))}

// 避免使用 index 作为 key（当列表会增删时）
{list.map((item, index) => (
  <View key={index}>  {/* ❌ */}
    {item.name}
  </View>
))}
```

---

## 14. 快速启动命令

### 开发环境

```bash
# 安装依赖
pnpm install

# H5 开发
pnpm dev:h5

# 微信小程序开发
pnpm dev:weapp

# React Native 开发
pnpm dev:rn
```

### 生产构建

```bash
# H5 构建
pnpm build:h5

# 微信小程序构建
pnpm build:weapp

# React Native 构建
pnpm build:rn
```

---

## 15. 学习资源

### 官方文档
- **Taro 官方文档**: https://taro-docs.jd.com/
- **React 官方文档**: https://react.dev/
- **Redux Toolkit**: https://redux-toolkit.js.org/

### 社区资源
- **Taro UI**: https://taro-ui.jd.com/ （UI组件库）
- **Taro GitHub**: https://github.com/NervJS/taro
- **Taro 论坛**: https://taro-club.jd.com/

---

## 总结

从 uni-app 转向 Taro React 的关键点：

1. ✅ **思维转换**：从 Vue 的"模板语法+双向绑定"转向 React 的"JSX+单向数据流"
2. ✅ **状态管理**：从 `data()` 转向 `useState`，从 `methods` 转向函数
3. ✅ **生命周期**：从 `onLoad/onShow` 转向 `useLoad/useDidShow` Hooks
4. ✅ **事件处理**：从 `@click` 转向 `onClick`，注意驼峰命名
5. ✅ **组件通信**：从 `props/$emit` 转向 `props/回调函数`
6. ✅ **TypeScript**：强烈建议使用，提升开发效率和代码质量

**学习建议：**
- 先熟悉 React Hooks（useState、useEffect、useCallback、useMemo）
- 理解 JSX 语法和单向数据流
- 多写代码，从简单页面开始练习
- 参考本项目的代码结构和实现方式

祝您学习顺利！🎉




