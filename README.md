# PureClip - 视频图片去水印系统

基于 FastAPI + Celery + MongoDB + MinIO + Taro 的全栈去水印解决方案。

## 📋 项目简介

PureClip 是一个功能强大的视频和图片去水印系统，支持多种去水印方法：

- **裁剪**：快速裁掉水印区域
- **模糊**：对水印区域进行高斯模糊
- **覆盖**：智能用周围颜色覆盖水印
- **填充**：使用AI算法智能修复水印区域

## 🏗️ 项目架构

```
用户上传URL
    ↓
[微信小程序 Taro]
    ↓
[FastAPI服务] → MongoDB (任务存储)
    ↓          → Redis (任务缓存)
[Celery Worker] 
    ↓
[ffmpeg/OpenCV] (视频/图片处理)
    ↓
[MinIO对象存储]
    ↓
返回处理结果URL
```

## 📂 项目结构

```
PureClip/
├── backend-watermark/          # 后端服务
│   ├── api/                    # API路由
│   ├── celery_app/             # Celery任务
│   ├── config/                 # 配置文件
│   ├── core/                   # 核心模块(MongoDB/Redis/MinIO)
│   ├── models/                 # 数据模型
│   ├── services/               # 业务服务
│   ├── app.py                  # FastAPI应用入口
│   └── requirements.txt        # Python依赖
│
├── frontend-watermark/         # 前端小程序
│   ├── config/                 # Taro配置
│   ├── src/
│   │   ├── pages/              # 页面
│   │   │   ├── index/          # 首页(上传)
│   │   │   ├── result/         # 处理结果页
│   │   │   └── history/        # 历史记录页
│   │   ├── services/           # API服务
│   │   ├── store/              # Redux状态管理
│   │   └── utils/              # 工具函数
│   └── package.json
│
└── README.md
```

## 🚀 快速开始

### 环境要求

**后端:**
- Python 3.8+
- MongoDB 4.4+
- Redis 6.0+
- MinIO
- FFmpeg
- OpenCV

**前端:**
- Node.js 16+
- pnpm 8+

### 1. 后端部署

#### 1.1 安装依赖

```bash
cd backend_watermark
pip install -r requirements.txt
```

#### 1.2 配置服务

编辑 `config/config.yaml`:

```yaml
# MongoDB配置
mongodb:
  uri: "mongodb://localhost:27017/"
  database: "pureclip"

# Redis配置
redis:
  host: "localhost"
  port: 6379

# MinIO配置
minio:
  endpoint: "localhost:9000"
  access_key: "your_access_key"
  secret_key: "your_secret_key"
```

#### 1.3 启动服务

```bash
# 启动FastAPI服务
python app.py

# 启动Celery Worker (新终端)
celery -A backend_watermark.celery_app.celery worker --loglevel=info

# 启动Celery Beat (可选，定时任务)
celery -A backend_watermark.celery_app.celery beat --loglevel=info
```

### 2. 前端部署

#### 2.1 安装依赖

```bash
cd frontend-watermark
pnpm install
```

#### 2.2 配置API地址

编辑 `src/config/api.ts`:

```typescript
export const API_BASE_URL = 'http://your-api-domain.com/api'
```

#### 2.3 启动开发

```bash
# H5开发
pnpm dev:h5

# 微信小程序开发
pnpm dev:weapp
# 然后使用微信开发者工具打开 dist 目录
```

#### 2.4 构建生产版本

```bash
# 构建H5
pnpm build:h5

# 构建微信小程序
pnpm build:weapp
```

## 📱 功能特性

### 1. 视频去水印
- 支持多种视频格式 (MP4, AVI, MOV等)
- 最大支持500MB视频
- 最长支持10分钟视频

### 2. 图片去水印
- 支持多种图片格式 (JPG, PNG, WebP等)
- 最大支持20MB图片
- 高质量输出

### 3. 多种去水印方法
- **裁剪**: 速度最快，适合边角水印
- **模糊**: 简单快速，让水印不明显
- **覆盖**: 用周围颜色自动填充
- **智能填充**: AI算法，效果最好

### 4. 任务管理
- 实时进度显示
- 任务状态轮询
- 历史记录查询

### 5. 文件管理
- MinIO对象存储
- 预签名URL访问
- 7天自动过期

## 🔧 技术栈

### 后端
- **FastAPI**: 现代化的Python Web框架
- **Celery**: 分布式任务队列
- **MongoDB**: NoSQL数据库
- **Redis**: 缓存和消息队列
- **MinIO**: S3兼容对象存储
- **FFmpeg**: 视频处理
- **OpenCV**: 图像处理

### 前端
- **Taro 4.0**: 多端开发框架
- **React 18**: UI框架
- **Redux Toolkit**: 状态管理
- **TypeScript**: 类型支持
- **Sass**: CSS预处理器

## 📖 API文档

### 创建任务

```http
POST /api/tasks
Content-Type: application/json

{
  "url": "https://example.com/video.mp4",
  "media_type": "video",
  "method": "crop",
  "watermark_region": {
    "x": 10,
    "y": 10,
    "width": 100,
    "height": 50
  },
  "user_id": "user_123"
}
```

### 查询任务状态

```http
GET /api/tasks/{task_id}
```

### 查询历史记录

```http
GET /api/history?user_id=user_123&limit=20
```

完整API文档：启动后端服务后访问 `http://localhost:8001/docs`

## 🔐 安全配置

生产环境请务必修改以下配置：

1. **MongoDB**: 使用强密码，开启认证
2. **Redis**: 设置密码，绑定内网IP
3. **MinIO**: 修改默认账号密码
4. **FastAPI**: 修改SECRET_KEY
5. **CORS**: 设置允许的域名

## 📊 性能优化

1. **Redis缓存**: 任务状态缓存24小时
2. **异步处理**: Celery异步任务队列
3. **流式传输**: 大文件分块上传下载
4. **CDN加速**: MinIO配合CDN使用

## 🐛 常见问题

### Q: FFmpeg未安装

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载并添加到PATH
```

### Q: OpenCV导入错误

```bash
pip install opencv-python opencv-contrib-python
```

### Q: Celery连接Redis失败

检查Redis是否启动：
```bash
redis-cli ping
```

### Q: MinIO连接失败

确保MinIO服务正常运行：
```bash
mc admin info local
```

## 📝 开发计划

- [ ] 支持批量处理
- [ ] AI智能检测水印位置
- [ ] 支持更多视频格式
- [ ] 视频压缩优化
- [ ] 用户系统和权限管理
- [ ] 微信模板消息通知
- [ ] 文件加密存储

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👥 联系方式

- Email: support@pureclip.com
- 项目主页: https://github.com/yourname/pureclip

---

**注意**: 本项目仅供学习交流使用，请勿用于商业用途或侵犯他人版权。




