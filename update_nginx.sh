#!/bin/bash
# Nginx配置更新脚本 - 添加MinIO反向代理

echo "==================================="
echo "PureClip Nginx配置更新"
echo "添加MinIO反向代理支持"
echo "==================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then 
    echo "❌ 请使用root用户运行此脚本"
    echo "   使用: sudo bash update_nginx.sh"
    exit 1
fi

# 备份原配置
echo "📦 备份原配置文件..."
cp /etc/nginx/conf.d/pureclip.conf /etc/nginx/conf.d/pureclip.conf.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ 备份完成: /etc/nginx/conf.d/pureclip.conf.backup.$(date +%Y%m%d_%H%M%S)"
echo ""

# 复制新配置
echo "📝 更新配置文件..."
cat > /etc/nginx/conf.d/pureclip.conf << 'EOF'
# HTTP -> HTTPS 重定向
server {
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
    access_log /var/log/nginx/pureclip_access.log;
    error_log  /var/log/nginx/pureclip_error.log;

    # 文件大小限制（视频文件较大）
    client_max_body_size 500M;

    # ===== MinIO 存储反向代理 (新增) =====
    location /storage/ {
        # 移除 /storage 前缀，直接访问 MinIO
        rewrite ^/storage/(.*) /$1 break;
        
        # 代理到本地 MinIO
        proxy_pass http://127.0.0.1:9000;
        proxy_http_version 1.1;
        
        # 标准代理头
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # MinIO 特定配置
        proxy_buffering off;
        proxy_request_buffering off;
        
        # 超时设置（大文件传输）
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
        
        # CORS 设置（允许小程序访问视频）
        add_header 'Access-Control-Allow-Origin' '*' always;
        add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
        add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
        add_header 'Access-Control-Expose-Headers' 'Content-Length,Content-Range' always;
        
        # OPTIONS 请求处理
        if ($request_method = 'OPTIONS') {
            add_header 'Access-Control-Allow-Origin' '*' always;
            add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS' always;
            add_header 'Access-Control-Allow-Headers' 'DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization' always;
            add_header 'Access-Control-Max-Age' 1728000 always;
            add_header 'Content-Type' 'text/plain; charset=utf-8' always;
            add_header 'Content-Length' 0 always;
            return 204;
        }
    }

    # ===== API 反向代理 (原有配置) =====
    location / {
        proxy_pass         http://127.0.0.1:8001;
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
}
EOF

echo "✅ 配置文件已更新"
echo ""

# 测试配置
echo "🧪 测试Nginx配置..."
nginx -t

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Nginx配置测试通过"
    echo ""
    
    # 重载Nginx
    echo "🔄 重载Nginx..."
    nginx -s reload
    
    if [ $? -eq 0 ]; then
        echo "✅ Nginx重载成功"
        echo ""
        echo "==================================="
        echo "✅ 配置更新完成！"
        echo "==================================="
        echo ""
        echo "📋 已添加的功能："
        echo "  ✅ MinIO反向代理: /storage/"
        echo "  ✅ 文件大小限制: 500MB"
        echo "  ✅ CORS支持: 已启用"
        echo ""
        echo "🔍 测试MinIO代理："
        echo "  curl https://api.pureclip.arbismart.cloud/storage/"
        echo ""
        echo "📁 备份文件："
        echo "  /etc/nginx/conf.d/pureclip.conf.backup.*"
        echo ""
    else
        echo "❌ Nginx重载失败"
        echo "   恢复备份: cp /etc/nginx/conf.d/pureclip.conf.backup.* /etc/nginx/conf.d/pureclip.conf"
        exit 1
    fi
else
    echo ""
    echo "❌ Nginx配置测试失败"
    echo "   恢复备份: cp /etc/nginx/conf.d/pureclip.conf.backup.* /etc/nginx/conf.d/pureclip.conf"
    exit 1
fi



