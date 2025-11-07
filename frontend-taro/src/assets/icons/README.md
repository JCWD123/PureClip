# TabBar 图标说明

## 📋 需要的图标文件

TabBar 需要以下图标文件（每个功能需要两个图标：普通状态和选中状态）：

### 当前需要的图标（2024年11月更新）：

1. **健康档案**
   - `profile.png` - 普通状态（建议使用：文档/档案图标）
   - `profile-active.png` - 选中状态

2. **作息提醒**
   - `rest.png` - 普通状态（建议使用：月亮/睡眠图标）
   - `rest-active.png` - 选中状态

3. **饮食建议**
   - `meal.png` - 普通状态（建议使用：餐具/食物图标）
   - `meal-active.png` - 选中状态

4. **天气推送**
   - `weather.png` - 普通状态（建议使用：云朵/天气图标）
   - `weather-active.png` - 选中状态

5. **养生妙招**
   - `health.png` - 普通状态（建议使用：叶子/心形图标）
   - `health-active.png` - 选中状态

## 📏 图标规格

- **尺寸**: 81px × 81px
- **格式**: PNG
- **背景**: 透明
- **颜色**: 
  - 普通状态：灰色（#666666）
  - 选中状态：蓝色（#1890ff）

## 🎨 获取图标

### 方式 1: 使用 iconfont（推荐）
1. 访问 [iconfont.cn](https://www.iconfont.cn/)
2. 搜索并下载对应的图标
3. 调整尺寸为 81×81
4. 导出为 PNG 格式

### 方式 2: 使用 Ant Design Icons
1. 访问 [Ant Design Icons](https://ant.design/components/icon-cn/)
2. 下载对应的 SVG 图标
3. 使用工具转换为 PNG（81×81）

### 方式 3: 暂时移除 TabBar
如果暂时无法准备图标，可以先移除 TabBar 配置进行开发测试。

## 🔄 临时解决方案

如果您想快速测试而没有图标，可以：

1. 将 `app.config-no-tabbar.ts` 的内容复制到 `app.config.ts`
2. 这样就移除了 TabBar，页面通过导航跳转访问

## 📱 使用文本 TabBar（无需图标）

修改 `app.config.ts`，移除 `iconPath` 和 `selectedIconPath`：

```typescript
tabBar: {
  color: '#666',
  selectedColor: '#1890ff',
  backgroundColor: '#fff',
  borderStyle: 'black',
  list: [
    {
      pagePath: 'pages/profile/index',
      text: '档案'
      // 移除 iconPath 和 selectedIconPath
    },
    // ... 其他项
  ]
}
```

> 注意：文字 TabBar 在小程序中可能显示效果不佳，建议还是使用图标。




