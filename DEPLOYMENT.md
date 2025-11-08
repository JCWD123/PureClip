# PureClip 部署指南

本文档详细说明如何在生产环境部署 PureClip 去水印系统。

## 📋 服务器要求

### 最低配置
- CPU: 2核
- 内存: 4GB
- 硬盘: 50GB
- 操作系统: Ubuntu 20.04+ / CentOS 7+ / Windows Server 2019+

### 推荐配置
- CPU: 4核+
- 内存: 8GB+
- 硬盘: 100GB+ SSD
- 操作系统: Ubuntu 22.04 LTS

## 🐧 Linux 部署

### 1. 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y git curl wget vim
```

### 2. 安装依赖服务

#### 2.1 安装Python 3.8+

```bash
sudo apt install -y python3 python3-pip python3-venv
python3 --version
```

#### 2.2 安装MongoDB

```bash
# 导入MongoDB公钥
wget -qO - https://www.mongodb.org/static/pgp/server-6.0.asc | sudo apt-key add -

# 添加MongoDB源
echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu focal/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list

# 安装MongoDB
sudo apt update
sudo apt install -y mongodb-org

# 启动MongoDB
sudo systemctl start mongod
sudo systemctl enable mongod

# 验证
sudo systemctl status mongod
```

#### 2.3 安装Redis

```bash
sudo apt install -y redis-server

# 配置Redis
sudo vim /etc/redis/redis.conf
# 修改: bind 127.0.0.1
# 添加: requirepass your_strong_password

# 重启Redis
sudo systemctl restart redis-server
sudo systemctl enable redis-server

# 验证
redis-cli ping
```

#### 2.4 安装MinIO

```bash
# 下载MinIO
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
sudo mv minio /usr/local/bin/

# 创建数据目录
sudo mkdir -p /data/minio

# 创建MinIO服务
sudo vim /etc/systemd/system/minio.service
```

添加以下内容：

```ini
[Unit]
Description=MinIO
Documentation=https://docs.min.io
Wants=network-online.target
After=network-online.target

[Service]
User=minio
Group=minio
WorkingDirectory=/usr/local/

Environment="MINIO_ROOT_USER=admin"
Environment="MINIO_ROOT_PASSWORD=your_strong_password"

ExecStart=/usr/local/bin/minio server /data/minio --console-address ":9001"

Restart=always
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

启动MinIO：

```bash
# 创建用户
sudo useradd -r minio -s /sbin/nologin
sudo chown -R minio:minio /data/minio

# 启动服务
sudo systemctl start minio
sudo systemctl enable minio

# 验证
sudo systemctl status minio
```

#### 2.5 安装FFmpeg

```bash
sudo apt install -y ffmpeg
ffmpeg -version
```

#### 2.6 安装OpenCV依赖

```bash
sudo apt install -y libsm6 libxext6 libxrender-dev libgomp1
```

### 3. 部署后端

#### 3.1 创建项目目录

```bash
sudo mkdir -p /opt/pureclip
sudo chown $USER:$USER /opt/pureclip
cd /opt/pureclip
```

#### 3.2 克隆代码

```bash
# 方式1: 从Git克隆
git clone https://github.com/yourname/pureclip.git .

# 方式2: 手动上传代码
# 使用 scp 或 SFTP 上传代码到 /opt/pureclip
```

#### 3.3 安装Python依赖

```bash
cd backend_watermark

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 3.4 配置服务

编辑 `config/config.yaml`：

```yaml
mongodb:
  uri: "mongodb://localhost:27017/"
  database: "pureclip"

redis:
  host: "localhost"
  port: 6379
  password: "your_redis_password"

minio:
  endpoint: "localhost:9000"
  access_key: "admin"
  secret_key: "your_minio_password"
  bucket_name: "pureclip"
  secure: false

server:
  host: "0.0.0.0"
  port: 8001
  debug: false  # 生产环境设为false
```

#### 3.5 创建Systemd服务

**FastAPI服务**

```bash
sudo vim /etc/systemd/system/pureclip-api.service
```

```ini
[Unit]
Description=PureClip FastAPI Service
After=network.target mongod.service redis-server.service minio.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/pureclip/backend-watermark
Environment="PATH=/opt/pureclip/backend-watermark/venv/bin"
Environment="PYTHONPATH=/opt/pureclip"
ExecStart=/opt/pureclip/backend-watermark/venv/bin/python app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Celery Worker服务**

```bash
sudo vim /etc/systemd/system/pureclip-celery.service
```

```ini
[Unit]
Description=PureClip Celery Worker
After=network.target redis-server.service

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/pureclip/backend-watermark
Environment="PATH=/opt/pureclip/backend-watermark/venv/bin"
Environment="PYTHONPATH=/opt/pureclip"
ExecStart=/opt/pureclip/backend-watermark/venv/bin/celery -A backend_watermark.celery_app.celery worker --loglevel=info --concurrency=4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 3.6 启动服务

```bash
# 创建临时目录
sudo mkdir -p /tmp/pureclip
sudo chown www-data:www-data /tmp/pureclip

# 重载systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start pureclip-api
sudo systemctl start pureclip-celery

# 设置开机自启
sudo systemctl enable pureclip-api
sudo systemctl enable pureclip-celery

# 查看状态
sudo systemctl status pureclip-api
sudo systemctl status pureclip-celery

# 查看日志
sudo journalctl -u pureclip-api -f
sudo journalctl -u pureclip-celery -f
```

### 4. 配置Nginx反向代理

```bash
sudo apt install -y nginx

sudo vim /etc/nginx/sites-available/pureclip
```

```nginx
upstream pureclip_api {
    server 127.0.0.1:8001;
}

server {
    listen 80;
    server_name api.pureclip.com;  # 修改为你的域名

    client_max_body_size 500M;

    location / {
        proxy_pass http://pureclip_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # 超时设置
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
    }
}
```

启用站点：

```bash
sudo ln -s /etc/nginx/sites-available/pureclip /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. 配置SSL证书 (可选)

```bash
# 安装Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d api.pureclip.com

# 自动续期
sudo certbot renew --dry-run
```

## 🪟 Windows 部署

### 1. 安装依赖

1. **Python 3.8+**: 从 [python.org](https://www.python.org/) 下载安装
2. **MongoDB**: 从 [mongodb.com](https://www.mongodb.com/) 下载安装
3. **Redis**: 从 [github.com/microsoftarchive/redis](https://github.com/microsoftarchive/redis) 下载
4. **MinIO**: 从 [min.io](https://min.io/) 下载
5. **FFmpeg**: 从 [ffmpeg.org](https://ffmpeg.org/) 下载并添加到PATH

### 2. 安装Python依赖

```cmd
cd backend-watermark
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置服务

编辑 `config/config.yaml` 修改相关配置

### 4. 启动服务

```cmd
REM 启动FastAPI
start_backend.bat

REM 启动Celery (新窗口)
start_celery.bat
```

### 5. 配置为Windows服务 (可选)

使用 NSSM 工具将Python应用注册为Windows服务。

## 🐳 Docker 部署

### 1. 创建 docker-compose.yml

```yaml
version: '3.8'

services:
  mongodb:
    image: mongo:6.0
    container_name: pureclip-mongodb
    restart: always
    ports:
      - "27017:27017"
    volumes:
      - mongodb_data:/data/db
    environment:
      MONGO_INITDB_ROOT_USERNAME: admin
      MONGO_INITDB_ROOT_PASSWORD: password

  redis:
    image: redis:7-alpine
    container_name: pureclip-redis
    restart: always
    ports:
      - "6379:6379"
    command: redis-server --requirepass your_redis_password

  minio:
    image: minio/minio:latest
    container_name: pureclip-minio
    restart: always
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: your_minio_password
    command: server /data --console-address ":9001"

  api:
    build: backend_watermark
    container_name: pureclip-api
    restart: always
    ports:
      - "8001:8001"
    depends_on:
      - mongodb
      - redis
      - minio
    environment:
      PYTHONPATH: /app
    volumes:
      - ./backend_watermark:/app
      - /tmp/pureclip:/tmp/pureclip

  celery:
    build: backend_watermark
    container_name: pureclip-celery
    restart: always
    depends_on:
      - redis
      - mongodb
      - minio
    environment:
      PYTHONPATH: /app
    volumes:
      - ./backend_watermark:/app
      - /tmp/pureclip:/tmp/pureclip
    command: celery -A backend_watermark.celery_app.celery worker --loglevel=info

volumes:
  mongodb_data:
  minio_data:
```

### 2. 启动服务

```bash
docker-compose up -d
docker-compose logs -f
```

## ⚙️ 性能优化

### 1. MongoDB优化

```javascript
// 创建索引
db.watermark_tasks.createIndex({ "task_id": 1 }, { unique: true })
db.watermark_tasks.createIndex({ "user_id": 1, "created_at": -1 })
db.process_history.createIndex({ "user_id": 1, "created_at": -1 })
```

### 2. Redis优化

```conf
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### 3. Nginx优化

```nginx
# worker进程数
worker_processes auto;

# 最大连接数
worker_connections 4096;

# 开启gzip
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript;
```

## 🔐 安全建议

1. **修改默认密码**: MongoDB、Redis、MinIO
2. **防火墙配置**: 只开放必要端口
3. **定期备份**: MongoDB数据、MinIO文件
4. **日志监控**: 使用ELK或其他日志系统
5. **限流配置**: Nginx限流防止攻击
6. **HTTPS**: 使用SSL证书
7. **定期更新**: 及时更新依赖包

## 📊 监控

### 1. 系统监控

使用 Prometheus + Grafana 监控系统资源

### 2. 应用监控

使用 Sentry 监控应用错误

### 3. 日志管理

使用 ELK Stack 收集和分析日志

## 🔄 更新部署

```bash
# 备份数据库
mongodump --db pureclip --out /backup/$(date +%Y%m%d)

# 拉取最新代码
cd /opt/pureclip
git pull

# 更新依赖
cd backend_watermark
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl restart pureclip-api
sudo systemctl restart pureclip-celery

# 查看状态
sudo systemctl status pureclip-api
sudo systemctl status pureclip-celery
```

## 🆘 故障排查

### 服务无法启动

```bash
# 查看日志
sudo journalctl -u pureclip-api -n 100
sudo journalctl -u pureclip-celery -n 100

# 查看端口占用
sudo netstat -tlnp | grep :8001

# 测试配置
cd /opt/pureclip/backend_watermark
source venv/bin/activate
python app.py
```

### MongoDB连接失败

```bash
# 检查MongoDB状态
sudo systemctl status mongod

# 测试连接
mongo --eval "db.adminCommand('ping')"
```

### Redis连接失败

```bash
# 检查Redis状态
sudo systemctl status redis-server

# 测试连接
redis-cli ping
```

---

如有问题，请查看 [FAQ](README.md#常见问题) 或提交 Issue。



