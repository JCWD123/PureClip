# 健康档案助手 Taro 版 - 快速启动指南

## 📋 前置条件

确保您的开发环境已安装：
- **Node.js** >= 16 （推荐 18+）
- **pnpm** >= 8 （或 npm/yarn）

验证安装：
```bash
node -v   # 应该显示 v16.0.0 或更高
pnpm -v   # 应该显示 8.0.0 或更高
```

## 🚀 5 分钟快速启动

### Step 1: 安装依赖

```bash
cd frontend-taro
pnpm install
```

如果没有安装 pnpm，可以先安装：
```bash
npm install -g pnpm
```

### Step 2: 配置 API 地址

编辑 `.env.development` 文件：
```bash
TARO_APP_API_URL=https://api.medai.medai-zjgsu.cn/api
```

> 注意：确保后端服务已启动在 `https://api.medai.medai-zjgsu.cn`

### Step 3: 启动开发服务器

#### 🌐 H5 开发（浏览器预览）

```bash
pnpm dev:h5
```

浏览器访问：`https://api.medai.medai-zjgsu.cn:3000`

#### 📱 微信小程序开发

1. 启动编译：
```bash
pnpm dev:weapp
```

2. 打开微信开发者工具，导入项目：
   - 选择 `frontend-taro/dist` 目录
   - 填写 AppID（测试可选择"测试号"）
   - 点击"导入"

3. 在微信开发者工具中预览和调试

## 🎯 开发流程

### 1. 创建新页面

#### 1.1 创建页面文件

在 `src/pages/` 下创建新目录，例如 `my-page/`：

```bash
mkdir src/pages/my-page
cd src/pages/my-page
```

创建三个文件：

**index.tsx** (页面组件)
```tsx
import { View, Text } from '@tarojs/components'
import './index.scss'

export default function MyPage() {
  return (
    <View className='my-page'>
      <Text>我的新页面</Text>
    </View>
  )
}
```

**index.scss** (样式)
```scss
.my-page {
  padding: 30px;
}
```

**index.config.ts** (页面配置)
```typescript
export default definePageConfig({
  navigationBarTitleText: '我的页面'
})

function definePageConfig(config: any) {
  return config
}
```

#### 1.2 注册页面路由

编辑 `src/app.config.ts`，添加页面路径：

```typescript
export default defineAppConfig({
  pages: [
    'pages/profile/index',
    'pages/my-page/index'  // 新增
  ],
  // ...其他配置
})
```

#### 1.3 跳转到新页面

```tsx
import Taro from '@tarojs/taro'

// 在任意页面中跳转
const handleNavigate = () => {
  Taro.navigateTo({
    url: '/pages/my-page/index'
  })
}
```

### 2. 调用 API

#### 2.1 在 `services/api.ts` 中定义 API

```typescript
export const getMyData = (userId: string) => {
  return request(`/my-data/${userId}`)
}
```

#### 2.2 在页面中调用

```tsx
import { useLoad } from '@tarojs/taro'
import { useState } from 'react'
import { getMyData } from '@/services/api'

export default function MyPage() {
  const [data, setData] = useState(null)

  useLoad(async () => {
    try {
      const result: any = await getMyData('user_123')
      setData(result.data)
    } catch (error) {
      console.error('加载数据失败:', error)
    }
  })

  return (
    <View>
      {data && <Text>{JSON.stringify(data)}</Text>}
    </View>
  )
}
```

### 3. 使用 Redux 管理状态

#### 3.1 创建 Slice

在 `store/` 下创建新的 slice：

```typescript
// store/mySlice.ts
import { createSlice, PayloadAction } from '@reduxjs/toolkit'

interface MyState {
  count: number
}

const initialState: MyState = {
  count: 0
}

const mySlice = createSlice({
  name: 'my',
  initialState,
  reducers: {
    increment: (state) => {
      state.count += 1
    },
    decrement: (state) => {
      state.count -= 1
    }
  }
})

export const { increment, decrement } = mySlice.actions
export default mySlice.reducer
```

#### 3.2 注册到 store

编辑 `store/index.ts`：

```typescript
import { configureStore } from '@reduxjs/toolkit'
import userReducer from './userSlice'
import myReducer from './mySlice'  // 新增

export const store = configureStore({
  reducer: {
    user: userReducer,
    my: myReducer  // 新增
  }
})

export type RootState = ReturnType<typeof store.getState>
export type AppDispatch = typeof store.dispatch
```

#### 3.3 在组件中使用

```tsx
import { useSelector, useDispatch } from 'react-redux'
import { RootState } from '@/store'
import { increment, decrement } from '@/store/mySlice'

export default function MyPage() {
  const count = useSelector((state: RootState) => state.my.count)
  const dispatch = useDispatch()

  return (
    <View>
      <Text>{count}</Text>
      <Button onClick={() => dispatch(increment())}>+1</Button>
      <Button onClick={() => dispatch(decrement())}>-1</Button>
    </View>
  )
}
```

## 🔧 常用开发技巧

### 1. 条件渲染

```tsx
// 方式1：三元表达式
{isLogin ? <Text>已登录</Text> : <Text>未登录</Text>}

// 方式2：逻辑与运算符
{isLogin && <Text>已登录</Text>}

// 方式3：立即执行函数（复杂条件）
{(() => {
  if (status === 'success') return <Text>成功</Text>
  if (status === 'error') return <Text>失败</Text>
  return <Text>加载中</Text>
})()}
```

### 2. 列表渲染

```tsx
const list = [
  { id: 1, name: '张三' },
  { id: 2, name: '李四' }
]

return (
  <View>
    {list.map(item => (
      <View key={item.id}>
        <Text>{item.name}</Text>
      </View>
    ))}
  </View>
)
```

### 3. 表单处理

```tsx
import { Input } from '@tarojs/components'
import { useState } from 'react'

export default function FormPage() {
  const [name, setName] = useState('')
  const [age, setAge] = useState(0)

  const handleSubmit = () => {
    console.log('提交数据:', { name, age })
  }

  return (
    <View>
      <Input
        value={name}
        onInput={(e) => setName(e.detail.value)}
        placeholder='请输入姓名'
      />
      <Input
        type='number'
        value={age.toString()}
        onInput={(e) => setAge(parseInt(e.detail.value) || 0)}
        placeholder='请输入年龄'
      />
      <Button onClick={handleSubmit}>提交</Button>
    </View>
  )
}
```

### 4. 生命周期 Hooks

```tsx
import { useLoad, useDidShow, useDidHide, useUnload } from '@tarojs/taro'
import { useEffect } from 'react'

export default function MyPage() {
  // 页面加载时（获取路由参数）
  useLoad((options) => {
    console.log('页面加载，参数:', options)
  })

  // 页面显示时（每次都会触发）
  useDidShow(() => {
    console.log('页面显示')
  })

  // 页面隐藏时
  useDidHide(() => {
    console.log('页面隐藏')
  })

  // 页面卸载时
  useUnload(() => {
    console.log('页面卸载')
  })

  // 组件挂载时（仅一次）
  useEffect(() => {
    console.log('组件挂载')
    return () => {
      console.log('组件卸载')
    }
  }, [])

  // 监听某个值变化
  useEffect(() => {
    console.log('count 变化了')
  }, [count])

  return <View>内容</View>
}
```

## 📱 多端编译

### H5 端

```bash
# 开发
pnpm dev:h5

# 构建
pnpm build:h5

# 预览构建结果
pnpm preview:h5
```

浏览器访问 `https://api.medai.medai-zjgsu.cn:3000`

### 微信小程序

```bash
# 开发（会持续监听文件变化）
pnpm dev:weapp

# 构建
pnpm build:weapp
```

使用微信开发者工具打开 `dist` 目录

### 其他小程序

```bash
# 支付宝小程序
pnpm dev:alipay

# 字节跳动小程序
pnpm dev:tt

# QQ小程序
pnpm dev:qq

# 百度小程序
pnpm dev:swan

# 京东小程序
pnpm dev:jd
```

### React Native

```bash
# 开发
pnpm dev:rn

# 构建
pnpm build:rn
```

> 注意：RN 需要额外配置原生开发环境（Android Studio / Xcode）

## 🐛 调试技巧

### H5 调试
- 使用浏览器开发者工具（F12）
- 查看 Network 检查 API 请求
- 使用 React DevTools 浏览器扩展

### 微信小程序调试
- 使用微信开发者工具的调试器
- 查看 Console 面板的日志输出
- 使用 Network 面板检查请求
- 真机调试：点击"预览"生成二维码

### 常用调试方法

```tsx
// 1. console.log 输出
console.log('调试信息:', data)

// 2. JSON.stringify 格式化对象
console.log('用户数据:', JSON.stringify(user, null, 2))

// 3. 在页面上显示调试信息
<View>{JSON.stringify(data)}</View>

// 4. Taro.showToast 快速提示
Taro.showToast({
  title: `当前值: ${value}`,
  icon: 'none'
})
```

## 📚 学习路径

1. **React 基础**
   - 阅读 React 官方文档：https://react.dev/
   - 掌握 useState、useEffect、useCallback、useMemo

2. **Taro 框架**
   - 阅读 Taro 官方文档：https://taro-docs.jd.com/
   - 了解多端差异和适配方案

3. **TypeScript**
   - 学习基础类型定义
   - 掌握接口（interface）和类型别名（type）

4. **Redux 状态管理**
   - Redux Toolkit 官方文档：https://redux-toolkit.js.org/

5. **实战练习**
   - 阅读本项目代码
   - 参考 `UNI_TO_TARO_GUIDE.md`（如果您有 uni-app 经验）

## ❓ 常见问题

**Q: pnpm install 失败？**
A: 尝试删除 `node_modules` 和 `pnpm-lock.yaml`，然后重新安装。

**Q: H5 端请求 API 跨域？**
A: 在开发环境中，可以配置代理。编辑 `config/dev.ts`：

```typescript
h5: {
  devServer: {
    proxy: {
      '/api': {
        target: 'https://api.medai.medai-zjgsu.cn',
        changeOrigin: true
      }
    }
  }
}
```

**Q: 微信小程序请求失败？**
A: 检查以下几点：
1. 微信开发者工具中是否勾选了"不校验合法域名"
2. API 地址是否正确
3. 后端是否允许跨域请求

**Q: 修改代码后没有生效？**
A: 重启开发服务器：
1. 停止当前进程（Ctrl + C）
2. 清除缓存：`rm -rf .temp dist`
3. 重新启动：`pnpm dev:h5` 或 `pnpm dev:weapp`

## 🎓 下一步

- ✅ 完成快速启动
- ✅ 创建第一个页面
- ✅ 调用 API 获取数据
- ✅ 使用 Redux 管理状态
- ✅ 多端编译测试
- 📚 阅读完整学习指南：`UNI_TO_TARO_GUIDE.md`

祝您开发顺利！🎉




