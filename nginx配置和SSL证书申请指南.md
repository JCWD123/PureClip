# Nginx配置和SSL证书申请指南

## 需求2：配置微信小程序API子域名

### 📋 配置概述

- **主域名**: `mirror-history-ai.com`
- **API子域名**: `api.pureclip.arbismart.cloud`
- **后端服务端口**: `8009`
- **SSL证书**: Let's Encrypt (通过Certbot申请)

---

## 🚀 实施步骤

### 步骤1：DNS配置

在你的域名DNS管理面板添加A记录：

```
类型: A
主机记录: api.arbismart
值: 你的服务器IP地址
TTL: 600
```

等待DNS生效（通常5-30分钟）：

```bash
# 验证DNS是否生效
nslookup api.pureclip.arbismart.cloud
```

---

### 步骤2：创建Nginx配置文件

创建配置文件：

```bash
sudo nano /etc/nginx/conf.d/arbismart.conf
```

粘贴以下配置：

```nginx
# /etc/nginx/conf.d/arbismart.conf

# HTTP -> HTTPS 重定向
server {
    listen 80;
    server_name api.pureclip.arbismart.cloud;

    # 自动跳转到 HTTPS
    return 301 https://$host$request_uri;
}

# HTTPS 主配置
server {
    listen 443 ssl http2;
    server_name api.pureclip.arbismart.cloud;

    # SSL 证书路径（Certbot自动申请后会自动填充）
    ssl_certificate     /etc/letsencrypt/live/api.pureclip.arbismart.cloud/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.pureclip.arbismart.cloud/privkey.pem;

    # SSL 配置
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_ciphers         HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # SSL Session 缓存
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    # 日志
    access_log /var/log/nginx/arbismart_access.log;
    error_log  /var/log/nginx/arbismart_error.log;

    # 反向代理配置
    location / {
        proxy_pass         http://127.0.0.1:8009;
        proxy_http_version 1.1;
        
        # WebSocket 支持
        proxy_set_header   Upgrade $http_upgrade;
        proxy_set_header   Connection "upgrade";
        
        # 标准代理头
        proxy_set_header   Host $host;
        proxy_set_header   X-Real-IP $remote_addr;
        proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header   X-Forwarded-Proto $scheme;
        
        # 超时设置（文档生成需要较长时间）
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;

        # CORS 设置（微信小程序调用）
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE' always;
        add_header Access-Control-Allow-Headers 'Content-Type,Authorization,X-Requested-With' always;
        add_header Access-Control-Max-Age 86400 always;

        # OPTIONS 请求处理
        if ($request_method = OPTIONS) {
            add_header Access-Control-Allow-Origin * always;
            add_header Access-Control-Allow-Methods 'GET, POST, OPTIONS, PUT, DELETE' always;
            add_header Access-Control-Allow-Headers 'Content-Type,Authorization,X-Requested-With' always;
            add_header Access-Control-Max-Age 86400 always;
            add_header Content-Type 'text/plain; charset=utf-8';
            add_header Content-Length 0;
            return 204;
        }
    }

    # 文件大小限制（用于上传证据等）
    client_max_body_size 20M;
}
```

---

### 步骤3：安装Certbot（如果尚未安装）

#### Ubuntu/Debian系统：

```bash
sudo apt update
sudo apt install certbot python3-certbot-nginx
```

#### CentOS/RHEL系统：

```bash
sudo yum install certbot python3-certbot-nginx
```

---

### 步骤4：申请SSL证书

**重要**：在申请证书前，先临时修改Nginx配置，注释掉SSL相关的配置：

```bash
# 编辑配置文件
sudo nano /etc/nginx/conf.d/arbismart.conf
```

临时修改为（申请证书时使用）：

```nginx
server {
    listen 80;
    server_name api.pureclip.arbismart.cloud;
    
    # Certbot验证路径
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://$host$request_uri;
    }
}
```

测试配置并重启Nginx：

```bash
sudo nginx -t
sudo systemctl restart nginx
```

申请证书：

```bash
sudo certbot certonly --nginx -d api.pureclip.arbismart.cloud
```

按照提示操作：
1. 输入邮箱地址（用于证书到期提醒）
2. 同意服务条款（输入 `Y`）
3. 是否订阅邮件（可选，输入 `N`）
4. 等待验证完成

成功后会显示：

```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/api.pureclip.arbismart.cloud/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/api.pureclip.arbismart.cloud/privkey.pem
```

---

### 步骤5：恢复完整Nginx配置

证书申请成功后，将Nginx配置恢复为完整版本（使用步骤2的配置），然后：

```bash
# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

---

### 步骤6：配置证书自动续期

Certbot会自动添加续期任务，验证一下：

```bash
# 测试自动续期
sudo certbot renew --dry-run

# 查看定时任务
sudo systemctl list-timers | grep certbot
```

手动续期证书（如需要）：

```bash
sudo certbot renew
sudo systemctl reload nginx
```

---

### 步骤7：修改后端服务端口（如需要）

如果你的后端服务不在8009端口，需要修改：

1. 修改后端启动命令：

```bash
cd /path/to/ArbiSmart/backend
python main_new.py --host 0.0.0.0 --port 8009
```

2. 或者修改Nginx配置中的`proxy_pass`端口

---

### 步骤8：修改前端API地址

更新前端代码中的API地址：

**文件**: `uni-app-frontend/src/pages/result/result.vue`

```javascript
// 修改前
const lawyerQRCodeUrl = ref('https://api.pureclip.arbismart.cloud:8009/contacts/律师微信二维码.jpg')

// 修改后
const lawyerQRCodeUrl = ref('https://api.pureclip.arbismart.cloud/contacts/律师微信二维码.jpg')
```

**文件**: `uni-app-frontend/src/pages/questionnaire/questionnaire.vue`（以及其他调用API的地方）

```javascript
// 修改API base URL
const response = await uni.request({
  url: 'https://api.pureclip.arbismart.cloud/api/documents/generate',
  // ...
})
```

建议创建一个统一的配置文件：

**文件**: `uni-app-frontend/src/config/api.js`

```javascript
// API配置
const ENV = 'production' // 'development' 或 'production'

const API_CONFIG = {
  development: {
    baseURL: 'https://api.pureclip.arbismart.cloud:8009',
    timeout: 600000
  },
  production: {
    baseURL: 'https://api.pureclip.arbismart.cloud',
    timeout: 600000
  }
}

export const API_BASE_URL = API_CONFIG[ENV].baseURL
export const API_TIMEOUT = API_CONFIG[ENV].timeout

// 辅助函数
export function getApiUrl(path) {
  return `${API_BASE_URL}${path}`
}
```

然后在代码中使用：

```javascript
import { getApiUrl } from '@/config/api'

const lawyerQRCodeUrl = ref(getApiUrl('/contacts/律师微信二维码.jpg'))
```

---

## 🧪 测试验证

### 1. 测试HTTP到HTTPS重定向

```bash
curl -I http://api.pureclip.arbismart.cloud
```

应该返回 `301 Moved Permanently` 并重定向到HTTPS

### 2. 测试HTTPS访问

```bash
curl -I https://api.pureclip.arbismart.cloud
```

应该返回 `200 OK`

### 3. 测试API接口

```bash
curl https://api.pureclip.arbismart.cloud/health
```

应该返回健康检查JSON

### 4. 测试静态文件访问

```bash
curl -I https://api.pureclip.arbismart.cloud/contacts/律师微信二维码.jpg
```

应该返回图片

### 5. 测试SSL证书

访问: https://www.ssllabs.com/ssltest/analyze.html?d=api.pureclip.arbismart.cloud

应该获得A级或以上评分

---

## 📊 监控和日志

### 查看访问日志

```bash
tail -f /var/log/nginx/arbismart_access.log
```

### 查看错误日志

```bash
tail -f /var/log/nginx/arbismart_error.log
```

### 查看证书信息

```bash
sudo certbot certificates
```

### 查看Nginx状态

```bash
sudo systemctl status nginx
```

---

## 🔧 常见问题

### Q1: 证书申请失败

**原因**: DNS未生效或端口80未开放

**解决**:
```bash
# 检查DNS
nslookup api.pureclip.arbismart.cloud

# 检查端口80
sudo netstat -tuln | grep :80

# 检查防火墙
sudo ufw status
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Q2: 反向代理502错误

**原因**: 后端服务未启动

**解决**:
```bash
# 检查后端服务
netstat -tuln | grep 8009

# 启动后端服务
cd /path/to/ArbiSmart/backend
python main_new.py --host 0.0.0.0 --port 8009
```

### Q3: CORS错误

**原因**: Nginx CORS配置不正确

**解决**: 确保Nginx配置中包含完整的CORS头部设置（见步骤2）

### Q4: 图片403或404错误

**原因**: 静态文件目录权限或路径问题

**解决**:
```bash
# 检查目录权限
ls -la /path/to/ArbiSmart/backend/contacts/

# 设置正确权限
sudo chmod 755 /path/to/ArbiSmart/backend/contacts/
sudo chmod 644 /path/to/ArbiSmart/backend/contacts/律师微信二维码.jpg
```

---

## 📝 微信小程序配置

在微信小程序管理后台配置服务器域名：

1. 登录 [微信公众平台](https://mp.weixin.qq.com)
2. 进入"开发" -> "开发管理" -> "开发设置"
3. 在"服务器域名"中添加：
   - **request合法域名**: `https://api.pureclip.arbismart.cloud`
   - **uploadFile合法域名**: `https://api.pureclip.arbismart.cloud`
   - **downloadFile合法域名**: `https://api.pureclip.arbismart.cloud`
4. 点击"保存并提交"

**注意**: 每月只能修改5次，请谨慎操作

---

## ✅ 验证清单

- [ ] DNS A记录已添加
- [ ] Nginx配置文件已创建
- [ ] Nginx配置测试通过 (`nginx -t`)
- [ ] SSL证书申请成功
- [ ] HTTPS访问正常
- [ ] API接口测试通过
- [ ] 静态文件访问正常
- [ ] 前端API地址已更新
- [ ] 微信小程序服务器域名已配置
- [ ] 证书自动续期已配置

---

## 🚀 部署命令速查

```bash
# 1. 创建Nginx配置
sudo nano /etc/nginx/conf.d/arbismart.conf

# 2. 测试配置
sudo nginx -t

# 3. 重启Nginx
sudo systemctl restart nginx

# 4. 申请SSL证书
sudo certbot certonly --nginx -d api.pureclip.arbismart.cloud

# 5. 再次测试和重启
sudo nginx -t
sudo systemctl restart nginx

# 6. 验证HTTPS
curl -I https://api.pureclip.arbismart.cloud/health

# 7. 查看证书
sudo certbot certificates
```

---

**配置完成后**: 
- ✅ 微信小程序可以通过 `https://api.pureclip.arbismart.cloud` 访问后端API
- ✅ SSL证书每3个月自动续期
- ✅ 所有HTTP请求自动重定向到HTTPS
- ✅ CORS已配置，微信小程序可正常调用

**最后更新**: 2025-10-02



























