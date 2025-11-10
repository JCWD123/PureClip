# 🌐 修复MinIO公网访问问题

## 🐛 问题

小程序无法访问返回的视频URL，因为URL是 `http://localhost:9000/...`

## ✅ 解决方案

使用你的API域名 `https://api.pureclip.arbismart.cloud` 通过Nginx反向代理MinIO。

---

## 📝 已完成的代码修改

### 1️⃣ 修改MinIO配置

**文件**: `backend_watermark/config/config.yaml`

```yaml
# MinIO对象存储配置
minio:
  endpoint: "api.pureclip.arbismart.cloud/storage"  # 通过Nginx代理
  access_key: "minioadmin"
  secret_key: "minioadmin"
  bucket_name: "pureclip"
  secure: true  # 使用HTTPS
  public_url: "https://api.pureclip.arbismart.cloud/storage"  # 公开访问URL
```

### 2️⃣ 更新配置加载

**文件**: `backend_watermark/config/config.py`

```python
# MinIO配置
MINIO_ENDPOINT: str = yaml_config["minio"]["endpoint"]
MINIO_ACCESS_KEY: str = yaml_config["minio"]["access_key"]
MINIO_SECRET_KEY: str = yaml_config["minio"]["secret_key"]
MINIO_BUCKET_NAME: str = yaml_config["minio"]["bucket_name"]
MINIO_SECURE: bool = yaml_config["minio"]["secure"]
MINIO_PUBLIC_URL: str = yaml_config["minio"].get("public_url", "")  # ← 新增
```

### 3️⃣ 修改MinIO客户端

**文件**: `backend_watermark/core/minio_client.py`

新增了 `_replace_with_public_url` 方法，自动将localhost替换为公开域名：

```python
def _replace_with_public_url(self, presigned_url: str, object_name: str) -> str:
    """将MinIO生成的URL替换为公开访问URL"""
    # 构建新的URL
    public_url = f"{settings.MINIO_PUBLIC_URL}/{settings.MINIO_BUCKET_NAME}/{object_name}"
    # 保留查询参数
    return public_url
```

---

## 🚀 部署步骤

### 第1步：配置Nginx反向代理

#### 方法A：添加到现有Nginx配置

```bash
# 编辑Nginx配置文件
sudo vim /etc/nginx/sites-available/pureclip

# 或直接添加到主配置
sudo vim /etc/nginx/nginx.conf
```

**添加以下配置**:

```nginx
server {
    listen 80;
    listen 443 ssl http2;
    server_name api.pureclip.arbismart.cloud;

    # SSL证书（必须配置）
    ssl_certificate /path/to/your/ssl/certificate.crt;
    ssl_certificate_key /path/to/your/ssl/private.key;

    # API路由
    location /api {
        proxy_pass http://localhost:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # MinIO存储路由（重要！）
    location /storage/ {
        rewrite ^/storage/(.*) /$1 break;
        
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        
        # 支持大文件
        client_max_body_size 500M;
        
        # CORS（允许小程序访问）
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, OPTIONS' always;
    }
}
```

#### 方法B：使用准备好的配置文件

```bash
# 复制配置文件
sudo cp nginx_minio.conf /etc/nginx/sites-available/pureclip

# 创建软链接
sudo ln -s /etc/nginx/sites-available/pureclip /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载Nginx
sudo nginx -s reload
```

### 第2步：修改MinIO配置连接到内网

**重要**：MinIO配置需要修改，因为现在通过Nginx代理。

#### 选项1：保持MinIO在localhost（推荐）

MinIO继续在localhost:9000运行，不需要改动MinIO本身。

但需要修改后端配置连接：

```bash
# 编辑 backend_watermark/config/config.yaml

# 修改为（内网连接）
minio:
  endpoint: "localhost:9000"  # ← 后端连接用localhost
  secure: false  # ← 内网不需要SSL
  public_url: "https://api.pureclip.arbismart.cloud/storage"  # ← 返回给前端用这个
```

**这样做的好处**：
- ✅ 后端通过localhost连接MinIO（快速、稳定）
- ✅ 返回给前端的URL是公网地址（可访问）
- ✅ 不需要修改MinIO配置

#### 选项2：配置MinIO的公网地址

如果MinIO需要知道自己的公网地址：

```bash
# 编辑MinIO启动脚本或配置
export MINIO_SERVER_URL="https://api.pureclip.arbismart.cloud/storage"
export MINIO_BROWSER_REDIRECT_URL="https://api.pureclip.arbismart.cloud/storage"

# 重启MinIO
sudo systemctl restart minio
```

### 第3步：重启所有服务

```bash
# 1. 重启Nginx
sudo nginx -s reload

# 2. 重启FastAPI（如果是systemd服务）
sudo systemctl restart pureclip-api

# 或手动重启
cd /root/PureClip/backend_watermark
python app.py

# 3. 重启Celery
sudo systemctl restart pureclip-celery

# 或手动重启
celery -A backend_watermark.celery_app.celery worker --loglevel=info
```

---

## 🧪 测试

### 测试1：API访问

```bash
curl https://api.pureclip.arbismart.cloud/api
# 应该返回：{"message":"欢迎使用PureClip去水印服务API"...}
```

### 测试2：MinIO访问

```bash
# 检查Nginx代理是否工作
curl https://api.pureclip.arbismart.cloud/storage/

# 应该返回MinIO的响应（可能是错误，但说明代理工作了）
```

### 测试3：提交任务并检查URL

```bash
# 提交一个任务
curl -X POST https://api.pureclip.arbismart.cloud/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://v.douyin.com/6YWKa6_haf8/",
    "media_type": "video",
    "method": "crop",
    "user_id": "test_user"
  }'

# 等待处理完成后查询
curl https://api.pureclip.arbismart.cloud/api/tasks/{task_id}

# 检查返回的result_url
# ✅ 应该是: https://api.pureclip.arbismart.cloud/storage/pureclip/video/...
# ❌ 不应该是: http://localhost:9000/...
```

---

## 📊 URL对比

### ❌ 修复前

```json
{
  "result_url": "http://localhost:9000/pureclip/video/xxx.mp4?X-Amz-..."
                     ^^^^^^^^^ 小程序无法访问
}
```

### ✅ 修复后

```json
{
  "result_url": "https://api.pureclip.arbismart.cloud/storage/pureclip/video/xxx.mp4?X-Amz-..."
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 小程序可以访问
}
```

---

## 🔍 故障排查

### 问题1: Nginx 502 Bad Gateway

**原因**: MinIO服务未启动或端口不对

**解决**:
```bash
# 检查MinIO是否运行
sudo systemctl status minio

# 检查端口
sudo netstat -tlnp | grep 9000

# 重启MinIO
sudo systemctl restart minio
```

### 问题2: 返回的URL仍是localhost

**原因**: 
1. 配置未生效（未重启服务）
2. public_url配置错误

**解决**:
```bash
# 1. 检查配置
cat backend_watermark/config/config.yaml | grep -A 5 "minio:"

# 2. 确认有public_url配置
# 3. 重启FastAPI和Celery

# 4. 查看日志确认
tail -f /var/log/pureclip/api.log
```

### 问题3: 视频仍无法播放

**原因**: 
1. MinIO bucket策略问题
2. CORS配置问题
3. SSL证书问题

**解决**:

```bash
# 1. 设置bucket为public
mc anonymous set download myminio/pureclip

# 2. 检查Nginx CORS配置是否添加

# 3. 测试直接访问视频URL
curl -I https://api.pureclip.arbismart.cloud/storage/pureclip/test.mp4
```

---

## 📱 微信小程序配置

**必须**在微信公众平台添加域名白名单：

1. 登录 https://mp.weixin.qq.com/
2. 开发 → 开发管理 → 开发设置 → 服务器域名
3. 添加：

**request合法域名**:
```
https://api.pureclip.arbismart.cloud
```

**downloadFile合法域名**:
```
https://api.pureclip.arbismart.cloud
```

**uploadFile合法域名**（如果需要）:
```
https://api.pureclip.arbismart.cloud
```

---

## 🎯 架构图

### 修复前

```
小程序 → API(https://api.pureclip.arbismart.cloud)
          ↓
小程序 ✗→ MinIO(http://localhost:9000) ← 无法访问
```

### 修复后

```
小程序 → API(https://api.pureclip.arbismart.cloud/api)
          ↓
小程序 → Nginx → MinIO(localhost:9000)
   (https://api.pureclip.arbismart.cloud/storage/...)
   ↑
   可以访问 ✓
```

---

## 📝 文件清单

### 已修改的文件

1. ✅ `backend_watermark/config/config.yaml` - MinIO配置
2. ✅ `backend_watermark/config/config.py` - 配置加载
3. ✅ `backend_watermark/core/minio_client.py` - URL替换逻辑

### 新增的文件

1. ✅ `nginx_minio.conf` - Nginx配置模板
2. ✅ `MINIO_PUBLIC_URL_FIX.md` - 本说明文档

---

## 🎉 完成检查清单

- [ ] 修改 `config.yaml` 添加 `public_url`
- [ ] 配置Nginx添加 `/storage/` 路由
- [ ] 重启Nginx
- [ ] 重启FastAPI
- [ ] 重启Celery
- [ ] 测试提交任务
- [ ] 检查返回的URL是否为公网地址
- [ ] 在小程序中测试视频是否能播放
- [ ] 添加域名到微信小程序白名单

---

## 💡 推荐配置

### 最佳实践配置

**backend_watermark/config/config.yaml**:

```yaml
minio:
  endpoint: "localhost:9000"  # 后端内网连接
  access_key: "minioadmin"
  secret_key: "minioadmin"
  bucket_name: "pureclip"
  secure: false  # 内网不需要SSL
  public_url: "https://api.pureclip.arbismart.cloud/storage"  # 公网访问URL
```

**优点**:
- ✅ 后端高效连接MinIO（localhost）
- ✅ 返回公网URL给前端
- ✅ 只需配置Nginx代理
- ✅ 无需修改MinIO本身

---

## 📖 相关文档

- 📘 `FRONTEND_VIDEO_FIX.md` - 前端视频播放修复
- 📘 `VIDEO_PARSER_SOLUTION.md` - 视频解析功能
- 📘 `IIILAB_CONFIG_DONE.md` - iiilab配置

---

**现在按照步骤配置Nginx并重启服务，视频就能在小程序中播放了！🎬**



