# 🚀 PureClip 前端构建和测试指南

## 📦 使用 pnpm 构建

### 1. 清理旧编译文件

```bash
cd frontend-watermark
rm -rf dist
```

### 2. 重新编译微信小程序

```bash
pnpm build:weapp
```

### 3. 开发模式（带热重载）

```bash
pnpm dev:weapp
```

---

## ✅ 完整构建流程

### 步骤1: 进入前端目录

```bash
cd frontend-watermark
```

### 步骤2: 清理旧文件（推荐）

```bash
# Windows
rmdir /s /q dist

# Linux/Mac
rm -rf dist
```

### 步骤3: 构建项目

```bash
# 生产环境构建
pnpm build:weapp

# 或开发环境（带热重载）
pnpm dev:weapp
```

### 步骤4: 微信开发者工具

1. 打开微信开发者工具
2. 导入项目：`frontend-watermark/dist`
3. 编译并查看效果

---

## 🧪 测试分享功能

### 测试前检查清单

- [ ] 已执行 `rm -rf dist` 清理旧文件
- [ ] 已执行 `pnpm build:weapp` 重新构建
- [ ] 微信开发者工具已刷新项目
- [ ] 控制台无报错

### 测试步骤

#### 测试1: 分享按钮

1. 进入"我的"页面
2. 点击"分享"按钮
3. **预期结果**: 
   - ✅ 立即弹出微信好友列表
   - ✅ 无 `TypeError` 报错
   - ✅ 可以选择好友发送

#### 测试2: 右上角分享

1. 在"我的"页面
2. 点击右上角"..."
3. 点击"转发"
4. **预期结果**:
   - ✅ 弹出好友列表
   - ✅ 分享卡片标题正确

#### 测试3: 查看控制台

在微信开发者工具的控制台查看:
- ✅ 无 `TypeError` 错误
- ✅ 无 `useShareAppMessage is not defined` 错误
- ✅ 无 `enableShareAppMessage` 相关警告

---

## 🔍 如果还是报错

### 问题排查步骤

#### 1. 检查 Taro 版本

```bash
cd frontend-watermark
pnpm list @tarojs/taro
```

**要求**: Taro >= 3.0.3

#### 2. 检查页面配置

**文件**: `src/pages/profile/index.config.ts`

确认包含:
```ts
export default {
  enableShareAppMessage: true  // ✅ 必须有这一行
}
```

#### 3. 检查组件代码

**文件**: `src/pages/profile/index.tsx`

确认包含:
```tsx
import { useShareAppMessage } from '@tarojs/taro'

export default function Profile() {
  // ✅ 在组件顶层调用
  useShareAppMessage(() => {
    return {
      title: 'PureClip去水印 - 快速去除视频水印',
      path: '/pages/index/index'
    }
  })
  
  return <View>...</View>
}
```

#### 4. 检查编译后的配置

```bash
# 查看编译后的页面配置
cat dist/pages/profile/index.json
```

**预期内容**:
```json
{
  "enableShareAppMessage": true,
  "navigationBarTitleText": "我的",
  ...
}
```

#### 5. 完全清理并重建

```bash
cd frontend-watermark

# 清理 node_modules（如果需要）
rm -rf node_modules
rm -rf dist

# 重新安装依赖
pnpm install

# 重新构建
pnpm build:weapp
```

---

## 📊 常见错误及解决方案

### 错误1: TypeError: l(...).shareAppMessage is not a function

**原因**:
- 缺少 `enableShareAppMessage: true` 配置
- Taro 版本过低（< 3.0.3）
- 未重新编译

**解决方案**:
```bash
# 1. 检查配置文件
cat src/pages/profile/index.config.ts

# 2. 清理并重新编译
rm -rf dist
pnpm build:weapp

# 3. 微信开发者工具刷新项目
```

### 错误2: useShareAppMessage is not defined

**原因**:
- 未正确导入 Hook
- 导入路径错误

**解决方案**:
```tsx
// ✅ 正确导入
import Taro, { useShareAppMessage } from '@tarojs/taro'

// ❌ 错误导入
import { useShareAppMessage } from '@tarojs/components'  // 错误！
```

### 错误3: 点击分享按钮无反应

**原因**:
- 按钮 `openType` 未设置为 `'share'`
- Hook 未正确调用

**解决方案**:
```tsx
// ✅ 正确
<Button openType='share'>分享</Button>

// ❌ 错误
<Button onClick={handleShare}>分享</Button>
```

### 错误4: 编译后配置未生效

**原因**:
- 未清理旧的编译文件
- 配置文件语法错误

**解决方案**:
```bash
# 完全清理并重新编译
cd frontend-watermark
rm -rf dist
pnpm build:weapp
```

---

## 🎯 验证成功的标志

### ✅ 构建成功

```bash
$ pnpm build:weapp

> frontend-watermark@1.0.0 build:weapp
> taro build --type weapp

✔ 编译成功
编译耗时: 5.234s
```

### ✅ 控制台无错误

微信开发者工具控制台:
- ✅ 无红色错误信息
- ✅ 无 `TypeError` 相关错误
- ✅ 页面正常加载

### ✅ 分享功能正常

- ✅ 点击"分享"按钮，立即弹出好友列表
- ✅ 点击右上角"转发"，显示转发选项
- ✅ 分享卡片标题和路径正确

---

## 📱 完整测试流程

### 1. 构建项目

```bash
cd frontend-watermark
rm -rf dist
pnpm build:weapp
```

### 2. 打开微信开发者工具

- 项目路径: `frontend-watermark/dist`
- 点击"编译"按钮

### 3. 测试分享

- 进入"我的"页面
- 点击"分享"按钮
- 验证弹出好友列表

### 4. 检查右上角分享

- 点击右上角"..."
- 查看是否有"转发"选项
- 点击"转发"验证功能

---

## 🔧 pnpm 相关命令

### 常用命令

```bash
# 安装依赖
pnpm install

# 开发模式（热重载）
pnpm dev:weapp

# 生产构建
pnpm build:weapp

# 查看依赖版本
pnpm list @tarojs/taro
pnpm list @tarojs/components

# 更新 Taro 到最新版本
pnpm update @tarojs/taro @tarojs/components @tarojs/runtime

# 清理缓存
pnpm store prune
```

### 调试命令

```bash
# 查看 Taro 配置
cat config/index.js

# 查看编译后的页面配置
cat dist/pages/profile/index.json

# 查看编译后的 app.json
cat dist/app.json
```

---

## 📖 相关文档

- [Taro Hooks 官方文档](https://nervjs.github.io/taro/docs/hooks/)
- [useShareAppMessage API](https://taro-docs.jd.com/docs/hooks#useshareappmessage)
- [微信小程序分享功能](https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/share.html)

---

## ✅ 最终检查

在提交前确认:

- [ ] 已清理 `dist` 目录
- [ ] 已执行 `pnpm build:weapp`
- [ ] 微信开发者工具已刷新
- [ ] 控制台无错误
- [ ] 分享按钮功能正常
- [ ] 右上角分享功能正常
- [ ] 分享卡片内容正确

---

**现在立即测试！** 🚀

```bash
cd frontend-watermark
rm -rf dist
pnpm build:weapp
```

然后在微信开发者工具中刷新项目，测试分享功能！



