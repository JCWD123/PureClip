# 🚀 Nginx配置更新指南 - 添加MinIO反向代理

## 📋 更新内容

在原有配置基础上添加：

1. ✅ MinIO反向代理（`/storage/` 路由）
2. ✅ 文件大小限制提升到500MB
3. ✅ CORS配置优化
4. ✅ 大文件传输优化

---

## 🎯 快速部署（2步）

### 方法1: 使用自动脚本（推荐）⭐⭐⭐⭐⭐

```bash
# 1. 赋予执行权限
chmod +x update_nginx.sh

# 2. 执行更新
sudo bash update_nginx.sh
```

**脚本会自动**：
- ✅ 备份原配置
- ✅ 更新配置文件
- ✅ 测试配置
- ✅ 重载Nginx

---

### 方法2: 手动更新

```bash
# 1. 备份原配置
sudo cp /etc/nginx/conf.d/pureclip.conf /etc/nginx/conf.d/pureclip.conf.backup

# 2. 复制新配置
sudo cp pureclip_with_minio.conf /etc/nginx/conf.d/pureclip.conf

# 3. 测试配置
sudo nginx -t

# 4. 重载Nginx
sudo nginx -s reload
```

---

## 🧪 测试

### 测试1: 检查Nginx配置

```bash
# 查看配置
cat /etc/nginx/conf.d/pureclip.conf | grep -A 5 "location /storage/"

# 应该看到：
# location /storage/ {
#     rewrite ^/storage/(.*) /$1 break;
#     proxy_pass http://127.0.0.1:9000;
#     ...
# }
```

### 测试2: 测试MinIO代理

```bash
# 测试MinIO是否可访问
curl -I https://api.pureclip.arbismart.cloud/storage/

# 应该返回MinIO的响应（可能是404或其他，但不是Nginx 502）
```

### 测试3: 提交任务测试

```bash
# 提交一个视频任务
curl -X POST https://api.pureclip.arbismart.cloud/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://v.douyin.com/6YWKa6_haf8/",
    "media_type": "video",
    "method": "crop",
    "user_id": "test_user"
  }'

# 获取task_id后查询
curl https://api.pureclip.arbismart.cloud/api/tasks/{task_id}

# 检查result_url是否为：
# https://api.pureclip.arbismart.cloud/storage/pureclip/video/...
```

---

## 📊 配置对比

### ❌ 更新前

```nginx
server {
    listen 443 ssl http2;
    
    # 只有API代理
    location / {
        proxy_pass http://127.0.0.1:8001;
    }
    
    client_max_body_size 20M;  # 太小
}
```

### ✅ 更新后

```nginx
server {
    listen 443 ssl http2;
    
    client_max_body_size 500M;  # ← 支持大视频
    
    # MinIO存储代理（新增）
    location /storage/ {
        rewrite ^/storage/(.*) /$1 break;
        proxy_pass http://127.0.0.1:9000;
        # ... CORS配置
    }
    
    # API代理（原有）
    location / {
        proxy_pass http://127.0.0.1:8001;
    }
}
```

---

## 🔧 关键变更

### 1. MinIO路由

```nginx
location /storage/ {
    rewrite ^/storage/(.*) /$1 break;
    proxy_pass http://127.0.0.1:9000;
}
```

**作用**：
- 访问 `https://api.pureclip.arbismart.cloud/storage/pureclip/xxx.mp4`
- 实际代理到 `http://127.0.0.1:9000/pureclip/xxx.mp4`

### 2. 文件大小限制

```nginx
client_max_body_size 500M;  # 从20M提升到500M
```

### 3. CORS配置

```nginx
add_header 'Access-Control-Allow-Origin' '*' always;
add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
```

**作用**：允许小程序跨域访问视频

---

## 🎯 URL映射

### 请求流程

```
小程序请求:
https://api.pureclip.arbismart.cloud/storage/pureclip/video/xxx.mp4
                                     ^^^^^^^^ /storage/ 路由
    ↓
Nginx接收并处理:
rewrite: /storage/pureclip/video/xxx.mp4 → /pureclip/video/xxx.mp4
                                            ^^^^^^^ 移除 /storage
    ↓
代理到MinIO:
http://127.0.0.1:9000/pureclip/video/xxx.mp4
                      ^^^^^^^^^^^^^^^^^^^^^^ 真实路径
    ↓
返回视频文件 ✅
```

---

## ⚠️ 故障排查

### 问题1: Nginx重载失败

```bash
# 查看错误
sudo nginx -t

# 检查语法错误
# 常见问题：缺少分号、括号不匹配
```

### 问题2: MinIO代理返回502

```bash
# 检查MinIO是否运行
sudo systemctl status minio

# 检查端口
sudo netstat -tlnp | grep 9000

# 启动MinIO
sudo systemctl start minio
```

### 问题3: 视频仍无法访问

```bash
# 1. 检查MinIO bucket策略
mc anonymous set download myminio/pureclip

# 2. 查看Nginx错误日志
sudo tail -f /var/log/nginx/pureclip_error.log

# 3. 查看Nginx访问日志
sudo tail -f /var/log/nginx/pureclip_access.log
```

---

## 📝 配置文件说明

### pureclip_with_minio.conf

完整的Nginx配置文件，包含：
- HTTP到HTTPS重定向
- SSL证书配置
- MinIO代理配置（新增）
- API代理配置
- CORS配置

### update_nginx.sh

自动更新脚本，功能：
- 自动备份原配置
- 更新配置文件
- 测试配置
- 重载Nginx
- 显示详细日志

---

## ✅ 完成检查清单

执行更新后，确认：

- [ ] Nginx重载成功
- [ ] `/storage/` 路由可访问
- [ ] MinIO服务正常运行
- [ ] 提交任务返回正确URL
- [ ] 小程序可以播放视频
- [ ] 下载功能正常工作

---

## 🎉 预期结果

### Celery日志

```log
✅ 文件上传成功: video/xxx.mp4
✅ 访问URL: https://api.pureclip.arbismart.cloud/storage/pureclip/video/xxx.mp4
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 公网地址
```

### API响应

```json
{
  "result_url": "https://api.pureclip.arbismart.cloud/storage/pureclip/video/xxx.mp4?X-Amz-..."
}
```

### 小程序

- ✅ 视频可以正常播放
- ✅ 下载到相册成功
- ✅ 复制链接功能正常

---

## 📖 相关文档

- 📘 `MINIO_PUBLIC_URL_FIX.md` - 完整解决方案
- 📘 `pureclip_with_minio.conf` - 新配置文件
- 📘 `update_nginx.sh` - 自动更新脚本

---

## 💡 注意事项

1. **备份重要**：脚本会自动备份，但建议手动也备份一份
2. **MinIO必须运行**：确保MinIO服务在9000端口运行
3. **SSL证书有效**：确保Let's Encrypt证书有效且未过期
4. **防火墙规则**：确保没有防火墙阻止MinIO访问

---

**现在运行 `sudo bash update_nginx.sh` 开始更新吧！🚀**



