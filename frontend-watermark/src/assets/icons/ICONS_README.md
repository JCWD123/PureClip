# 📱 底部导航图标说明

## 需要的图标文件

```
assets/icons/
├── home.png              # 去水印（未选中）
├── home-active.png       # 去水印（选中）
├── history.png           # 历史（未选中）
├── history-active.png    # 历史（选中）
├── profile.png           # 我的（未选中）
└── profile-active.png    # 我的（选中）
```

## 图标规格

- **尺寸**: 81x81 px（推荐）或 108x108 px
- **格式**: PNG（透明背景）
- **风格**: 简约线条图标
- **颜色**: 
  - 未选中: 灰色 `#666`
  - 选中: 紫色 `#667eea`

---

## 🎨 快速获取图标

### 方法1: iconfont.cn（推荐）⭐

1. 访问 https://www.iconfont.cn/
2. 搜索关键词：
   - "home" 或 "首页" → home.png
   - "history" 或 "历史" → history.png
   - "user" 或 "我的" → profile.png
3. 下载PNG格式（81x81 或 108x108）
4. 准备两个版本（灰色和彩色）

### 方法2: IconPark

1. 访问 https://iconpark.oceanengine.com/
2. 搜索图标
3. 自定义颜色
4. 下载PNG

### 方法3: 使用Emoji（临时方案）

如果暂时没有图标，可以使用emoji表情作为临时图标。

**注意**: 小程序不支持直接使用emoji作为tabBar图标，必须使用图片文件。

---

## 🖼️ 推荐的图标样式

### home（去水印）
- 建议图标: 剪刀✂️、魔法棒🪄、橡皮擦、清理工具
- 关键词: scissors, magic-wand, eraser, clean

### history（历史）
- 建议图标: 时钟⏰、列表📋、历史记录
- 关键词: clock, history, list, time

### profile（我的）
- 建议图标: 用户👤、个人中心、账户
- 关键词: user, profile, account, person

---

## 📝 临时解决方案

如果急需测试，可以使用以下方式：

### 选项1: 使用纯色图标

创建简单的几何形状图标：
- 圆形
- 方形
- 三角形

可以用任何图像编辑工具（如画图、Photoshop、Figma）快速创建。

### 选项2: 截图法

1. 找一个有类似图标的网站或APP
2. 截图图标部分
3. 裁剪成正方形
4. 调整大小到81x81

---

## 🎨 使用AI生成图标

可以使用以下AI工具生成图标：

### Midjourney提示词

```
simple icon, home icon, minimalist, flat design, 
white background, PNG, app icon style --ar 1:1
```

### Stable Diffusion提示词

```
simple flat icon, minimalist app icon, clean design,
monochrome, transparent background, vector style
```

---

## 📐 手动创建图标（Figma/Sketch）

### 步骤：

1. **创建画布**
   - 尺寸: 81x81 px
   - 背景: 透明

2. **绘制图标**
   - 使用简单的几何形状
   - 线条粗细: 2-3px
   - 圆角: 2-4px

3. **导出**
   - 格式: PNG
   - 透明背景
   - 2x和3x分辨率（可选）

---

## ✅ 检查清单

部署前确认：

- [ ] 所有6个图标文件都已准备
- [ ] 图标尺寸一致（推荐81x81）
- [ ] PNG格式，透明背景
- [ ] 文件名正确（与配置一致）
- [ ] 放在正确的目录（`src/assets/icons/`）

---

## 🚀 使用图标

图标准备好后，放在以下目录：

```bash
frontend-watermark/src/assets/icons/
├── home.png
├── home-active.png
├── history.png
├── history-active.png
├── profile.png
└── profile-active.png
```

然后编译小程序：

```bash
cd frontend-watermark
npm run build:weapp
```

---

**如果实在找不到合适的图标，可以先使用纯色方块作为占位，后续再替换！**

