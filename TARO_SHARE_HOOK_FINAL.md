# ✅ Taro 分享功能 - Hook 写法（最终方案）

## 🎯 根据 Taro 官方文档实现

参考文档：
- [Taro Hooks 官方文档](https://nervjs.github.io/taro/docs/hooks/)
- [useShareAppMessage API](https://taro-docs.jd.com/docs/hooks#useshareappmessage)

---

## ✅ 完整实现代码

### 步骤1: 页面配置文件

**文件**: `frontend-watermark/src/pages/profile/index.config.ts`

```ts
export default {
  navigationBarTitleText: '我的',
  navigationBarBackgroundColor: '#667eea',
  navigationBarTextStyle: 'white' as const,
  enableShareAppMessage: true  // ✅ 必须启用！
}
```

**关键**: `enableShareAppMessage: true` 必须设置，否则分享功能不生效！

---

### 步骤2: 页面组件（Hook 写法）

**文件**: `frontend-watermark/src/pages/profile/index.tsx`

```tsx
import { View, Button, Switch } from '@tarojs/components'
import Taro, { useShareAppMessage } from '@tarojs/taro'
import { useState, useEffect } from 'react'
import './index.scss'

export default function Profile() {
  const [showSmartTips, setShowSmartTips] = useState(true)
  const [userId] = useState('8759892')

  // ✅ 页面分享配置（Hooks 写法）
  useShareAppMessage(() => {
    return {
      title: 'PureClip去水印 - 快速去除视频水印',
      path: '/pages/index/index'
    }
  })

  useEffect(() => {
    const savedTips = Taro.getStorageSync('showSmartTips')
    if (savedTips !== undefined) {
      setShowSmartTips(savedTips)
    }
  }, [])

  const handleSmartTipsChange = (e: any) => {
    const value = e.detail.value
    setShowSmartTips(value)
    Taro.setStorageSync('showSmartTips', value)
    
    Taro.showToast({
      title: value ? '已开启智能提示' : '已关闭智能提示',
      icon: 'none',
      duration: 1500
    })
  }

  const handleHistoryClick = () => {
    Taro.switchTab({ url: '/pages/history/index' })
  }

  const handleHelpClick = () => {
    Taro.showModal({
      title: '使用帮助',
      content: '1. 复制视频链接\n2. 粘贴到首页输入框\n3. 点击"一键去水印"\n4. 等待2-5秒完成解析\n5. 播放或下载无水印视频\n\n支持平台：抖音、快手、小红书、百度等',
      confirmText: '知道了',
      showCancel: false
    })
  }

  return (
    <View className='profile-page'>
      {/* 用户信息 */}
      <View className='user-header'>
        <View className='user-avatar'>
          <View className='avatar-placeholder'>👤</View>
        </View>
        <View className='user-info'>
          <View className='user-name'>用户 {userId}</View>
          <View className='user-desc'>普通会员</View>
        </View>
      </View>

      {/* 功能列表 */}
      <View className='menu-container'>
        {/* 解析记录 */}
        <View className='menu-item' onClick={handleHistoryClick}>
          <View className='menu-left'>
            <View className='menu-icon'>📋</View>
            <View className='menu-text'>解析记录</View>
          </View>
          <View className='menu-arrow'>›</View>
        </View>

        {/* 使用帮助 */}
        <View className='menu-item' onClick={handleHelpClick}>
          <View className='menu-left'>
            <View className='menu-icon'>❓</View>
            <View className='menu-text'>使用帮助</View>
          </View>
          <View className='menu-arrow'>›</View>
        </View>

        {/* ✅ 分享按钮 - 触发 useShareAppMessage */}
        <Button className='menu-item-button' openType='share'>
          <View className='menu-item'>
            <View className='menu-left'>
              <View className='menu-icon'>📤</View>
              <View className='menu-text'>分享</View>
            </View>
            <View className='menu-arrow'>›</View>
          </View>
        </Button>

        {/* 联系客服 */}
        <Button className='menu-item-button' openType='contact'>
          <View className='menu-item'>
            <View className='menu-left'>
              <View className='menu-icon'>👥</View>
              <View className='menu-text'>联系客服</View>
            </View>
            <View className='menu-arrow'>›</View>
          </View>
        </Button>
      </View>

      {/* 智能提示开关 */}
      <View className='settings-container'>
        <View className='setting-item'>
          <View className='setting-left'>
            <View className='setting-icon'>💡</View>
            <View className='setting-text'>智能提示弹框</View>
          </View>
          <Switch
            className='setting-switch'
            checked={showSmartTips}
            onChange={handleSmartTipsChange}
            color='#667eea'
          />
        </View>
      </View>

      {/* 版本信息 */}
      <View className='footer-info'>
        <View className='version-text'>PureClip v1.0.0</View>
        <View className='copyright-text'>快速去水印，简单高效</View>
      </View>
    </View>
  )
}
```

---

## 🔑 关键点说明

### 1. 导入 useShareAppMessage

```tsx
import Taro, { useShareAppMessage } from '@tarojs/taro'
```

**必须从 `@tarojs/taro` 导入！**

### 2. 在组件顶层调用 Hook

```tsx
export default function Profile() {
  // ✅ 必须在组件顶层调用
  useShareAppMessage(() => {
    return {
      title: 'PureClip去水印 - 快速去除视频水印',
      path: '/pages/index/index'
    }
  })
  
  // ... 其他代码
}
```

**注意**:
- ✅ 必须在组件函数的顶层调用
- ❌ 不能在条件语句中调用
- ❌ 不能在循环中调用
- ❌ 不能在回调函数中调用

### 3. 返回分享配置对象

```tsx
useShareAppMessage(() => {
  return {
    title: '分享标题',      // 必填
    path: '/pages/index/index',  // 必填，分享路径
    imageUrl: '/assets/share.jpg'  // 可选，分享图片
  }
})
```

### 4. 分享按钮

```tsx
<Button openType='share'>
  点击分享
</Button>
```

**作用**:
- 点击按钮 → 自动触发 `useShareAppMessage` → 获取分享配置 → 弹出微信好友列表

---

## 🎨 高级用法

### 根据分享来源返回不同内容

```tsx
useShareAppMessage((res) => {
  console.log('分享来源:', res.from)  // 'button' 或 'menu'
  
  if (res.from === 'button') {
    // 点击页面分享按钮
    return {
      title: '我的好友推荐：PureClip去水印',
      path: '/pages/index/index'
    }
  } else {
    // 点击右上角菜单分享
    return {
      title: 'PureClip去水印 - 快速去水印工具',
      path: '/pages/index/index'
    }
  }
})
```

### 动态分享内容

```tsx
export default function Result() {
  const [videoTitle, setVideoTitle] = useState('')
  const [videoCover, setVideoCover] = useState('')

  useShareAppMessage(() => {
    return {
      title: videoTitle || '我用PureClip去除了视频水印',
      path: '/pages/index/index',
      imageUrl: videoCover
    }
  })

  // ... 其他代码
}
```

### 带参数的分享路径

```tsx
useShareAppMessage(() => {
  return {
    title: 'PureClip去水印',
    path: '/pages/index/index?from=share&userId=123'
  }
})
```

---

## 📋 完整配置清单

### ✅ 必须完成的配置

1. **页面配置启用分享**
   ```ts
   // index.config.ts
   export default {
     enableShareAppMessage: true
   }
   ```

2. **导入 Hook**
   ```tsx
   import { useShareAppMessage } from '@tarojs/taro'
   ```

3. **在组件顶层调用 Hook**
   ```tsx
   export default function MyPage() {
     useShareAppMessage(() => ({ ... }))
   }
   ```

4. **返回配置对象**
   ```tsx
   return {
     title: '...',
     path: '...'
   }
   ```

5. **使用分享按钮**
   ```tsx
   <Button openType='share'>分享</Button>
   ```

---

## 🚫 常见错误

### ❌ 错误1: 忘记启用分享

```ts
// ❌ 错误：缺少 enableShareAppMessage
export default {
  navigationBarTitleText: '我的'
}
```

**结果**: 分享功能不生效，点击无反应

**正确做法**:
```ts
export default {
  navigationBarTitleText: '我的',
  enableShareAppMessage: true  // ✅ 必须添加
}
```

### ❌ 错误2: Hook 使用位置错误

```tsx
// ❌ 错误：在条件语句中使用
export default function MyPage() {
  if (someCondition) {
    useShareAppMessage(() => { ... })  // 错误！
  }
}
```

**正确做法**:
```tsx
// ✅ 正确：在顶层使用
export default function MyPage() {
  useShareAppMessage(() => { ... })  // 正确！
  
  if (someCondition) {
    // ...
  }
}
```

### ❌ 错误3: 没有返回对象

```tsx
// ❌ 错误：没有 return
useShareAppMessage(() => {
  {
    title: '...',
    path: '...'
  }
})
```

**正确做法**:
```tsx
// ✅ 正确：必须 return
useShareAppMessage(() => {
  return {
    title: '...',
    path: '...'
  }
})
```

### ❌ 错误4: 缺少必填字段

```tsx
// ❌ 错误：缺少 path
useShareAppMessage(() => {
  return {
    title: '...'
  }
})
```

**正确做法**:
```tsx
// ✅ 正确：title 和 path 都必填
useShareAppMessage(() => {
  return {
    title: '...',
    path: '/pages/index/index'
  }
})
```

---

## 📊 API 参数详解

### useShareAppMessage 回调参数

```ts
interface ShareAppMessageRes {
  from: 'button' | 'menu'  // 分享来源
  target: any              // 如果是 button 触发，target 是 button 元素
  webViewUrl?: string      // 如果是 web-view 分享，返回 webview 的 url
}
```

### 返回对象参数

```ts
interface ShareAppMessageReturn {
  title: string           // 必填，分享标题
  path: string            // 必填，分享路径
  imageUrl?: string       // 可选，分享图片
}
```

**图片规格**:
- 尺寸: 500x400 px (5:4 比例)
- 格式: JPG/PNG
- 大小: < 128KB
- 位置: 本地路径或线上 URL

---

## 🧪 测试步骤

### 1. 清理旧编译文件

```bash
cd frontend-watermark
rm -rf dist
```

### 2. 重新编译

```bash
npm run build:weapp
```

### 3. 微信开发者工具测试

**测试分享按钮**:
1. 打开"我的"页面
2. 点击"分享"按钮
3. **预期**: 立即弹出微信好友列表 ✅

**测试右上角分享**:
1. 点击页面右上角"..."
2. 点击"转发"
3. **预期**: 弹出微信好友列表 ✅

### 4. 查看控制台

确保没有以下错误:
- ❌ `TypeError: l(...).shareAppMessage is not a function`
- ❌ `useShareAppMessage is not defined`
- ❌ `enableShareAppMessage is required`

---

## 🎯 版本要求

### Taro 版本

```json
{
  "@tarojs/taro": "^3.0.3",
  "@tarojs/components": "^3.0.3",
  "@tarojs/runtime": "^3.0.3"
}
```

**最低要求**: Taro 3.0.3+

### 微信小程序基础库

**最低要求**: 2.0.0+

**推荐版本**: 2.10.0+

### 查看版本

```bash
# 查看 Taro 版本
npm list @tarojs/taro

# 微信开发者工具中查看基础库版本
# 设置 -> 项目设置 -> 调试基础库
```

---

## 📱 多页面分享配置

### 首页分享

**文件**: `src/pages/index/index.config.ts`
```ts
export default {
  navigationBarTitleText: '去水印',
  enableShareAppMessage: true
}
```

**文件**: `src/pages/index/index.tsx`
```tsx
import { useShareAppMessage } from '@tarojs/taro'

export default function Index() {
  useShareAppMessage(() => ({
    title: 'PureClip去水印 - 快速去除视频水印',
    path: '/pages/index/index'
  }))
  
  return <View>...</View>
}
```

### 结果页分享

**文件**: `src/pages/result/index.config.ts`
```ts
export default {
  navigationBarTitleText: '处理结果',
  enableShareAppMessage: true
}
```

**文件**: `src/pages/result/index.tsx`
```tsx
import { useShareAppMessage } from '@tarojs/taro'
import { useState } from 'react'

export default function Result() {
  const [videoInfo, setVideoInfo] = useState({
    title: '',
    cover: ''
  })

  useShareAppMessage(() => ({
    title: videoInfo.title || '我用PureClip去除了视频水印',
    path: '/pages/index/index',
    imageUrl: videoInfo.cover
  }))
  
  return <View>...</View>
}
```

---

## 🎉 预期效果

### 用户操作流程

```
用户点击"分享"按钮
    ↓
触发 useShareAppMessage Hook
    ↓
获取分享配置 { title, path }
    ↓
微信弹出好友列表 ✨
    ↓
选择好友/群聊
    ↓
发送分享卡片 ✅
    ↓
好友点击进入小程序
```

### 分享卡片样式

```
┌─────────────────────────────┐
│                             │
│  [小程序默认图标]            │
│                             │
│  PureClip去水印              │
│  快速去除视频水印            │
│                             │
│  小程序                      │
│                             │
└─────────────────────────────┘
```

---

## 🔍 调试技巧

### 查看分享配置

```tsx
useShareAppMessage((res) => {
  console.log('分享触发:', res)
  console.log('分享来源:', res.from)
  
  const config = {
    title: 'PureClip去水印',
    path: '/pages/index/index'
  }
  
  console.log('返回配置:', config)
  return config
})
```

### 检查页面配置

在微信开发者工具中:
1. 打开"详情"
2. 查看"基本信息"
3. 确认 `enableShareAppMessage` 为 `true`

### 查看编译后代码

```bash
# 查看编译后的配置
cat dist/pages/profile/index.json
```

**预期内容**:
```json
{
  "enableShareAppMessage": true,
  "navigationBarTitleText": "我的"
}
```

---

## ✅ 验证清单

完成以下检查后，分享功能应该完全正常：

- [ ] `index.config.ts` 添加 `enableShareAppMessage: true`
- [ ] 从 `@tarojs/taro` 导入 `useShareAppMessage`
- [ ] 在组件顶层调用 `useShareAppMessage`
- [ ] 回调函数返回对象包含 `title` 和 `path`
- [ ] 使用 `<Button openType='share'>` 触发分享
- [ ] 清理旧编译文件 `rm -rf dist`
- [ ] 重新编译 `npm run build:weapp`
- [ ] 微信开发者工具无报错
- [ ] 点击分享按钮弹出好友列表 ✅
- [ ] 分享卡片内容正确 ✅

---

## 🚀 立即测试

```bash
cd frontend-watermark

# 清理旧编译文件
rm -rf dist

# 重新编译
npm run build:weapp

# 在微信开发者工具中刷新项目
```

---

**完成！** Hook 写法已完全实现，按照 Taro 官方文档标准！✨

如果还有问题，请检查：
1. Taro 版本是否 >= 3.0.3
2. 微信基础库版本是否 >= 2.0.0
3. `enableShareAppMessage: true` 是否已配置
4. 是否清理并重新编译了项目


