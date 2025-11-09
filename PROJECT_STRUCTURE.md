# PureClip 项目结构说明

本文档详细说明了项目的完整结构和各个文件的作用。

## 📁 完整目录结构

```
PureClip/
│
├── backend-watermark/                   # 后端服务目录
│   ├── api/                             # API路由模块
│   │   ├── __init__.py                  # 导出路由
│   │   ├── task.py                      # 任务管理API
│   │   └── history.py                   # 历史记录API
│   │
│   ├── celery_app/                      # Celery异步任务
│   │   ├── __init__.py
│   │   ├── celery.py                    # Celery应用配置
│   │   └── tasks.py                     # 任务处理逻辑
│   │
│   ├── config/                          # 配置文件
│   │   ├── __init__.py
│   │   ├── config.py                    # 配置类
│   │   └── config.yaml                  # YAML配置文件
│   │
│   ├── core/                            # 核心模块
│   │   ├── __init__.py
│   │   ├── mongodb.py                   # MongoDB连接管理
│   │   ├── redis_client.py              # Redis客户端
│   │   └── minio_client.py              # MinIO客户端
│   │
│   ├── models/                          # 数据模型
│   │   ├── __init__.py
│   │   └── task.py                      # 任务数据模型
│   │
│   ├── services/                        # 业务服务
│   │   ├── __init__.py
│   │   ├── downloader.py                # 文件下载服务
│   │   ├── video_processor.py           # 视频处理服务
│   │   └── image_processor.py           # 图片处理服务
│   │
│   ├── __init__.py                      # 包初始化
│   ├── app.py                           # FastAPI应用入口
│   ├── requirements.txt                 # Python依赖
│   ├── start_backend.sh                 # Linux/Mac启动脚本
│   ├── start_backend.bat                # Windows启动脚本
│   ├── start_celery.sh                  # Celery启动脚本(Linux)
│   └── start_celery.bat                 # Celery启动脚本(Windows)
│
├── frontend-watermark/                  # 前端小程序目录
│   ├── config/                          # Taro配置
│   │   ├── index.ts                     # 主配置
│   │   ├── dev.ts                       # 开发环境配置
│   │   └── prod.ts                      # 生产环境配置
│   │
│   ├── src/                             # 源代码
│   │   ├── assets/                      # 静态资源
│   │   │   └── icons/                   # 图标
│   │   │       └── README.md            # 图标说明
│   │   │
│   │   ├── config/                      # 配置
│   │   │   └── api.ts                   # API配置
│   │   │
│   │   ├── pages/                       # 页面
│   │   │   ├── index/                   # 首页(上传)
│   │   │   │   ├── index.tsx
│   │   │   │   ├── index.scss
│   │   │   │   └── index.config.ts
│   │   │   │
│   │   │   ├── result/                  # 处理结果页
│   │   │   │   ├── index.tsx
│   │   │   │   ├── index.scss
│   │   │   │   └── index.config.ts
│   │   │   │
│   │   │   └── history/                 # 历史记录页
│   │   │       ├── index.tsx
│   │   │       ├── index.scss
│   │   │       └── index.config.ts
│   │   │
│   │   ├── services/                    # API服务
│   │   │   └── api.ts                   # API接口封装
│   │   │
│   │   ├── store/                       # Redux状态管理
│   │   │   ├── index.ts                 # Store配置
│   │   │   └── taskSlice.ts             # 任务状态切片
│   │   │
│   │   ├── utils/                       # 工具函数
│   │   │   └── request.ts               # HTTP请求封装
│   │   │
│   │   ├── app.tsx                      # 应用入口
│   │   ├── app.scss                     # 全局样式
│   │   └── app.config.ts                # 应用配置
│   │
│   ├── babel.config.js                  # Babel配置
│   ├── package.json                     # 项目依赖
│   ├── project.config.json              # 小程序配置
│   ├── tsconfig.json                    # TypeScript配置
│   ├── start_dev.sh                     # Linux/Mac启动脚本
│   └── start_dev.bat                    # Windows启动脚本
│
├── .gitignore                           # Git忽略文件
├── README.md                            # 项目说明文档
├── QUICKSTART.md                        # 快速开始指南
├── DEPLOYMENT.md                        # 部署指南
└── PROJECT_STRUCTURE.md                 # 本文档
```

## 🔍 关键文件说明

### 后端核心文件

#### 1. `backend-watermark/app.py`
- **作用**: FastAPI应用入口
- **功能**: 
  - 初始化FastAPI应用
  - 配置CORS
  - 注册API路由
  - 管理应用生命周期
- **端口**: 8001

#### 2. `backend-watermark/config/config.yaml`
- **作用**: 主要配置文件
- **配置项**:
  - MongoDB连接
  - Redis连接
  - MinIO配置
  - Celery配置
  - 视频处理参数
  - 图片处理参数

#### 3. `backend-watermark/celery_app/tasks.py`
- **作用**: Celery异步任务
- **核心任务**:
  - `process_watermark_task`: 处理去水印任务
  - 下载原始文件
  - 调用处理服务
  - 上传结果到MinIO
  - 更新任务状态

#### 4. `backend-watermark/services/video_processor.py`
- **作用**: 视频处理服务
- **支持方法**:
  - `_crop_watermark`: 裁剪去水印
  - `_blur_watermark`: 模糊去水印
  - `_cover_watermark`: 覆盖去水印
  - `_inpaint_watermark`: 智能填充去水印

#### 5. `backend-watermark/services/image_processor.py`
- **作用**: 图片处理服务
- **支持方法**: 与视频处理相同

### 前端核心文件

#### 1. `frontend-watermark/src/pages/index/index.tsx`
- **作用**: 首页(上传页面)
- **功能**:
  - 输入视频/图片URL
  - 选择媒体类型
  - 选择去水印方法
  - 创建处理任务

#### 2. `frontend-watermark/src/pages/result/index.tsx`
- **作用**: 处理结果页
- **功能**:
  - 实时显示处理进度
  - 轮询任务状态
  - 显示处理结果
  - 复制链接/下载文件

#### 3. `frontend-watermark/src/pages/history/index.tsx`
- **作用**: 历史记录页
- **功能**:
  - 显示处理历史
  - 复制结果链接
  - 删除历史记录

#### 4. `frontend-watermark/src/services/api.ts`
- **作用**: API接口封装
- **接口**:
  - `taskApi.createTask`: 创建任务
  - `taskApi.getTask`: 查询任务状态
  - `taskApi.listTasks`: 获取任务列表
  - `historyApi.getHistory`: 获取历史记录

#### 5. `frontend-watermark/src/store/taskSlice.ts`
- **作用**: Redux状态管理
- **状态**:
  - `currentTask`: 当前任务
  - `taskList`: 任务列表
  - `history`: 历史记录

## 🔄 数据流详解

### 完整处理流程

```
1. 用户在小程序输入URL和参数
   ↓
2. 前端调用 taskApi.createTask()
   ↓
3. FastAPI创建任务记录
   - 生成task_id
   - 存入MongoDB
   - 缓存到Redis
   ↓
4. 提交Celery异步任务
   ↓
5. Celery Worker处理:
   a. 更新状态为 DOWNLOADING
   b. 调用Downloader下载文件
   c. 更新状态为 PROCESSING
   d. 调用VideoProcessor/ImageProcessor处理
   e. 更新状态为 UPLOADING
   f. 上传到MinIO
   g. 更新状态为 COMPLETED
   h. 保存处理历史
   ↓
6. 前端轮询获取任务状态
   ↓
7. 显示处理结果和下载链接
```

### 数据存储

**MongoDB集合:**
- `watermark_tasks`: 任务记录
- `process_history`: 处理历史

**Redis键:**
- `task:{task_id}`: 任务状态缓存(24小时)

**MinIO对象:**
- `video/{task_id}/result.mp4`: 处理后的视频
- `image/{task_id}/result.jpg`: 处理后的图片

## 🛠️ 技术栈详解

### 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.109.0 | Web框架 |
| Celery | 5.3.6 | 异步任务队列 |
| MongoDB | 6.0+ | 数据存储 |
| Redis | 7.0+ | 缓存&消息队列 |
| MinIO | latest | 对象存储 |
| FFmpeg | latest | 视频处理 |
| OpenCV | 4.9.0 | 图像处理 |

### 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Taro | 4.0.6 | 多端框架 |
| React | 18.3.1 | UI框架 |
| Redux Toolkit | 2.2.5 | 状态管理 |
| TypeScript | 5.4.5 | 类型支持 |
| Sass | latest | CSS预处理 |

## 📊 API端点列表

### 任务管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/tasks | 创建任务 |
| GET | /api/tasks/{task_id} | 查询任务状态 |
| GET | /api/tasks | 获取任务列表 |
| DELETE | /api/tasks/{task_id} | 删除任务 |

### 历史记录

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | /api/history | 获取历史记录 |
| DELETE | /api/history/{history_id} | 删除历史记录 |

### 系统

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | / | 根路径 |
| GET | /health | 健康检查 |
| GET | /docs | API文档 |

## 🎨 页面路由

### 小程序路由

| 路径 | 页面 | 说明 |
|------|------|------|
| /pages/index/index | 首页 | 上传和参数配置 |
| /pages/result/index | 结果页 | 显示处理进度和结果 |
| /pages/history/index | 历史页 | 查看处理历史 |

## 🔧 配置项说明

### 后端配置 (config.yaml)

```yaml
# MongoDB配置
mongodb:
  uri: MongoDB连接字符串
  database: 数据库名
  collection_tasks: 任务集合名
  collection_history: 历史集合名

# Redis配置
redis:
  host: Redis主机
  port: Redis端口
  db: 数据库编号
  password: Redis密码

# MinIO配置
minio:
  endpoint: MinIO端点
  access_key: 访问密钥
  secret_key: 密钥
  bucket_name: 存储桶名
  secure: 是否使用HTTPS

# Celery配置
celery:
  broker_url: 消息队列URL
  result_backend: 结果存储URL

# 视频处理配置
video:
  max_size_mb: 最大文件大小(MB)
  max_duration_seconds: 最大时长(秒)
  output_format: 输出格式
  temp_dir: 临时目录

# 超时配置
timeout:
  download: 下载超时(秒)
  process: 处理超时(秒)
  upload: 上传超时(秒)
```

### 前端配置

**API配置** (`src/config/api.ts`):
```typescript
export const API_BASE_URL = 'API服务地址'
```

**小程序配置** (`project.config.json`):
```json
{
  "appid": "微信小程序AppID",
  "projectname": "项目名称"
}
```

## 📝 开发规范

### Python代码规范
- 使用 PEP 8 编码规范
- 类型注解使用 typing
- 异步函数使用 async/await
- 日志使用 logging 模块

### TypeScript代码规范
- 使用 ESLint + Prettier
- 函数组件使用 React Hooks
- 状态管理使用 Redux Toolkit
- 样式使用 Sass/SCSS

### 命名规范
- **后端**: snake_case (变量、函数)
- **前端**: camelCase (变量、函数)
- **组件**: PascalCase
- **常量**: UPPER_CASE

## 🧪 测试

### 后端测试
```bash
cd backend_watermark
pytest tests/
```

### 前端测试
```bash
cd frontend-watermark
pnpm test
```

## 📦 打包部署

### 后端打包
```bash
# 生成requirements.txt
pip freeze > requirements.txt

# Docker打包
docker build -t pureclip-backend .
```

### 前端打包
```bash
cd frontend-watermark

# H5打包
pnpm build:h5

# 小程序打包
pnpm build:weapp
```

## 🔐 安全注意事项

1. **敏感信息**: 不要将 `config.yaml` 提交到Git
2. **密码管理**: 使用强密码并定期更新
3. **访问控制**: 配置防火墙和IP白名单
4. **HTTPS**: 生产环境必须使用HTTPS
5. **用户认证**: 实现用户登录和权限管理

## 📈 性能优化建议

1. **MongoDB索引**: 为常用查询字段创建索引
2. **Redis缓存**: 合理设置缓存过期时间
3. **CDN加速**: MinIO配合CDN使用
4. **负载均衡**: 使用Nginx做负载均衡
5. **异步处理**: 耗时操作都使用Celery异步

## 🐛 问题排查

### 查看日志
```bash
# 后端日志
sudo journalctl -u pureclip-api -f

# Celery日志
sudo journalctl -u pureclip-celery -f

# Nginx日志
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 调试模式
```yaml
# config.yaml
server:
  debug: true  # 开启调试模式
```

---

**文档版本**: 1.0.0  
**最后更新**: 2025-11-06  
**维护者**: PureClip Team





