# PureClip 快速开始指南

欢迎使用 PureClip 去水印系统！本指南将帮助你在 5 分钟内启动项目。

## 📋 前置要求

### 必须安装
- **Python 3.8+** - 后端运行环境
- **Node.js 16+** - 前端运行环境
- **MongoDB** - 数据存储
- **Redis** - 缓存和任务队列
- **MinIO** - 对象存储
- **FFmpeg** - 视频处理
- **pnpm** - 前端包管理器

### 快速安装命令

**Ubuntu/Debian:**
```bash
# 安装Python和基础工具
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# 安装Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 安装pnpm
npm install -g pnpm

# 安装MongoDB
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update && sudo apt install -y mongodb-org

# 安装Redis
sudo apt install -y redis-server

# 安装FFmpeg
sudo apt install -y ffmpeg

# 安装OpenCV依赖
sudo apt install -y libsm6 libxext6 libxrender-dev libgomp1
```

**macOS:**
```bash
# 使用Homebrew安装
brew install python node pnpm mongodb-community redis ffmpeg opencv
```

**Windows:**
- 从官网下载安装 Python、Node.js
- 使用 `npm install -g pnpm` 安装 pnpm
- 从官网下载安装 MongoDB、Redis for Windows、FFmpeg

## 🚀 5分钟快速启动

### 步骤1: 启动依赖服务

**Linux/macOS:**
```bash
# 启动MongoDB
sudo systemctl start mongod
# 或
mongod --dbpath ~/data/db

# 启动Redis
sudo systemctl start redis
# 或
redis-server

# 启动MinIO (简化版)
mkdir -p ~/minio/data
minio server ~/minio/data --console-address ":9001"
```

**Windows:**
```cmd
REM 启动MongoDB
net start MongoDB

REM 启动Redis
redis-server

REM 启动MinIO
minio.exe server C:\minio\data --console-address ":9001"
```

### 步骤2: 启动后端

打开新终端：

**Linux/macOS:**
```bash
cd backend_watermark

# 安装依赖（首次运行）
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 使用启动脚本
./start_backend.sh
```

**Windows:**
```cmd
cd backend-watermark

REM 安装依赖（首次运行）
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

REM 使用启动脚本
start_backend.bat
```

### 步骤3: 启动Celery Worker

打开新终端：

**Linux/macOS:**
```bash
cd backend_watermark
source venv/bin/activate
./start_celery.sh
```

**Windows:**
```cmd
cd backend-watermark
venv\Scripts\activate
start_celery.bat
```

### 步骤4: 启动前端

打开新终端：

**Linux/macOS:**
```bash
cd frontend-watermark

# 安装依赖（首次运行）
pnpm install

# 使用启动脚本
./start_dev.sh
```

**Windows:**
```cmd
cd frontend-watermark

REM 安装依赖（首次运行）
pnpm install

REM 使用启动脚本
start_dev.bat
```

选择启动模式：
- **选项1**: H5模式 - 浏览器访问 `http://localhost:3000`
- **选项2**: 微信小程序 - 用微信开发者工具打开 `dist` 目录

## ✅ 验证安装

### 1. 检查后端API

```bash
# 测试API健康检查
curl http://localhost:8001/health

# 查看API文档
浏览器访问: http://localhost:8001/docs
```

预期输出：
```json
{
  "status": "healthy",
  "service": "pureclip-watermark-remover"
}
```

### 2. 检查Celery Worker

在Celery终端应该看到：
```
[tasks]
  . backend_watermark.celery_app.tasks.process_watermark_task
```

### 3. 测试前端

- **H5模式**: 浏览器访问 `http://localhost:3000`
- **小程序模式**: 微信开发者工具中应该能看到小程序界面

## 🎯 第一次使用

### 1. 在首页输入测试URL

示例视频URL:
```
https://www.w3schools.com/html/mov_bbb.mp4
```

### 2. 选择去水印方法

- **裁剪** - 最快速，适合边角水印
- **模糊** - 简单处理
- **覆盖** - 智能填充
- **智能填充** - 效果最好

### 3. 点击"开始处理"

### 4. 查看处理结果

- 实时查看处理进度
- 完成后可以复制链接或下载文件
- 在历史记录页面查看所有处理记录

## 🔧 配置说明

### 后端配置

编辑 `backend-watermark/config/config.yaml`:

```yaml
# MongoDB配置
mongodb:
  uri: "mongodb://localhost:27017/"
  database: "pureclip"

# Redis配置
redis:
  host: "localhost"
  port: 6379
  password: null  # 如果Redis设置了密码，在这里填写

# MinIO配置
minio:
  endpoint: "localhost:9000"
  access_key: "minioadmin"
  secret_key: "minioadmin"
  bucket_name: "pureclip"
  secure: false

# 服务器配置
server:
  host: "0.0.0.0"
  port: 8001
  debug: true  # 生产环境改为false
```

### 前端配置

编辑 `frontend-watermark/src/config/api.ts`:

```typescript
// 开发环境
export const API_BASE_URL = 'http://localhost:8001/api'

// 生产环境
// export const API_BASE_URL = 'https://api.pureclip.arbismart.cloud/api'
```

## 📱 微信小程序配置

### 1. 获取AppID

在[微信公众平台](https://mp.weixin.qq.com/)注册小程序账号，获取AppID

### 2. 修改项目配置

编辑 `frontend-watermark/project.config.json`:

```json
{
  "appid": "你的AppID",
  "projectname": "pureclip-watermark-remover"
}
```

### 3. 配置服务器域名

在微信公众平台后台配置：

- **request合法域名**: `https://api.pureclip.com`
- **uploadFile合法域名**: `https://api.pureclip.com`
- **downloadFile合法域名**: `https://minio.pureclip.com`

注意：本地开发时可以在微信开发者工具中勾选"不校验合法域名"

## 🐛 常见问题

### Q1: Celery连接Redis失败

**错误**: `Error: Couldn't connect to Redis`

**解决**:
```bash
# 检查Redis是否运行
redis-cli ping
# 应该返回 PONG

# 检查Redis配置
# 确保config.yaml中的Redis配置正确
```

### Q2: MongoDB连接失败

**错误**: `MongoDB连接失败`

**解决**:
```bash
# 检查MongoDB是否运行
sudo systemctl status mongod

# 或直接启动
mongod --dbpath ~/data/db
```

### Q3: FFmpeg not found

**错误**: `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**解决**:
```bash
# Linux
sudo apt install ffmpeg

# macOS
brew install ffmpeg

# Windows
# 下载FFmpeg并添加到系统PATH
```

### Q4: 前端无法连接后端

**检查**:
1. 后端是否正常运行: `curl http://localhost:8001/health`
2. 前端API配置是否正确
3. 防火墙是否阻止连接

### Q5: Celery Worker无法处理任务

**检查**:
1. Celery Worker是否正常运行
2. 查看Celery日志输出
3. Redis连接是否正常
4. FFmpeg和OpenCV是否正确安装

## 📖 下一步

- 📚 阅读[完整文档](README.md)了解更多功能
- 🚀 查看[部署指南](DEPLOYMENT.md)进行生产部署
- 🔧 根据需求修改配置文件
- 🎨 自定义前端UI样式
- 📊 配置监控和日志系统

## 💡 开发建议

1. **开发环境**: 保持 `debug: true`
2. **生产环境**: 设置 `debug: false` 并配置日志
3. **安全**: 修改所有默认密码
4. **性能**: 根据服务器配置调整Celery并发数
5. **监控**: 使用日志系统监控错误和性能

## 📞 获取帮助

- 查看[API文档](http://localhost:8001/docs)
- 阅读[完整README](README.md)
- 提交[Issue](https://github.com/yourname/pureclip/issues)
- 加入开发者社区

---

🎉 恭喜！你已经成功启动 PureClip 去水印系统！

现在可以开始处理你的第一个视频或图片了。






