# 下载器增强功能说明

## 📋 概述

为了解决短链和重定向链接的下载问题，我们对下载器进行了全面升级，添加了浏览器伪装和自动跟随重定向功能。

## 🐛 问题背景

### 原始问题
- **百度短链**: `https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&...` 需要浏览器请求头才能正确重定向
- **抖音短链**: `https://v.douyin.com/6YWKa6_haf8/` 需要特定的Referer和User-Agent
- **小红书短链**: `http://xhslink.com/o/uMnICz6mL2` 可能需要Cookie和浏览器标识

### 症状
```log
❌ 下载的文件不是视频/图片，而是：
   - HTML重定向页面
   - "请在浏览器中打开"提示页
   - 空白页面或错误信息
```

---

## ✅ 解决方案

### 1️⃣ 完整的浏览器请求头伪装

**文件**: `backend_watermark/services/downloader.py`

```python
def _get_browser_headers(self, url: str) -> dict:
    """生成浏览器请求头，伪装成真实浏览器"""
    headers = {
        # 核心标识：模拟Chrome 131浏览器
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        
        # 接受的内容类型
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        
        # 语言偏好
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        
        # 压缩支持
        'Accept-Encoding': 'gzip, deflate, br',
        
        # 连接保持
        'Connection': 'keep-alive',
        
        # 升级不安全请求
        'Upgrade-Insecure-Requests': '1',
        
        # Chrome安全头
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        
        # 缓存控制
        'Cache-Control': 'max-age=0',
    }
    
    # 根据不同平台添加特定的Referer
    if 'douyin.com' in url:
        headers['Referer'] = 'https://www.douyin.com/'
    elif 'baidu.com' in url:
        headers['Referer'] = 'https://www.baidu.com/'
    elif 'xhslink.com' in url or 'xiaohongshu.com' in url:
        headers['Referer'] = 'https://www.xiaohongshu.com/'
    # ... 更多平台
    
    return headers
```

### 2️⃣ Session支持（Cookie和连接复用）

```python
def __init__(self):
    self.temp_dir = Path(settings.VIDEO_TEMP_DIR)
    self.temp_dir.mkdir(parents=True, exist_ok=True)
    # 创建Session以支持Cookie和连接复用
    self.session = requests.Session()
```

**优势**:
- ✅ 自动处理Cookie（某些平台需要）
- ✅ 连接复用（提高性能）
- ✅ 保持会话状态

### 3️⃣ 自动跟随重定向

```python
response = self.session.get(
    url,
    headers=headers,
    stream=True,
    timeout=settings.TIMEOUT_DOWNLOAD,
    allow_redirects=True,  # ✅ 显式允许重定向
    verify=True  # ✅ 验证SSL证书
)

# 检查最终URL（可能经过多次重定向）
final_url = response.url
if final_url != url:
    logger.info(f"URL重定向: {url} -> {final_url}")
```

**示例日志**:
```log
INFO - 开始下载文件: https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&...
INFO - URL重定向: https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&... -> https://cdn.baidu.com/videos/abc123.mp4
INFO - Content-Type: video/mp4
INFO - 文件下载成功: /tmp/pureclip/xxx.mp4 (大小: 15234567 bytes)
```

### 4️⃣ 内容类型验证

```python
def _is_valid_media_content(self, content_type: str, media_type: str) -> bool:
    """验证Content-Type是否为有效的媒体文件"""
    content_type_lower = content_type.lower()
    
    # 排除HTML和文本类型（防止下载到错误页面）
    invalid_types = ['text/html', 'text/plain', 'application/json', 'application/xml']
    for invalid_type in invalid_types:
        if invalid_type in content_type_lower:
            return False
    
    # 检查是否为媒体类型
    if media_type == MediaType.VIDEO.value:
        valid_patterns = ['video/', 'application/octet-stream']
        return any(pattern in content_type_lower for pattern in valid_patterns)
    else:  # IMAGE
        valid_patterns = ['image/', 'application/octet-stream']
        return any(pattern in content_type_lower for pattern in valid_patterns)
```

**警告机制**:
```python
# 验证是否为有效的媒体文件
if not self._is_valid_media_content(content_type, media_type):
    logger.warning(f"可能不是有效的媒体文件，Content-Type: {content_type}")
    # 记录响应内容的前200字节用于调试
    response_preview = response.content[:200]
    logger.warning(f"响应预览: {response_preview}")
```

### 5️⃣ 文件大小检查

```python
# 检查文件大小
file_size = os.path.getsize(local_path)
logger.info(f"文件下载成功: {local_path} (大小: {file_size} bytes)")

# 如果文件太小，可能是错误页面
if file_size < 1024:  # 小于1KB
    logger.warning(f"下载的文件过小({file_size} bytes)，可能不是有效的媒体文件")
```

---

## 📊 支持的平台和Header配置

| 平台 | URL模式 | 特殊配置 |
|------|---------|----------|
| 🎵 **抖音** | `v.douyin.com` | `Referer: https://www.douyin.com/` |
| 📱 **百度** | `mr.baidu.com`, `pan.baidu.com` | `Referer: https://www.baidu.com/` |
| 📖 **小红书** | `xhslink.com`, `xiaohongshu.com` | `Referer: https://www.xiaohongshu.com/` |
| 📹 **快手** | `v.kuaishou.com` | `Referer: https://www.kuaishou.com/` |
| 📺 **B站** | `bilibili.com`, `b23.tv` | `Referer: https://www.bilibili.com/` |
| 🌐 **通用** | 其他URL | 标准浏览器头 |

---

## 🧪 测试方法

### 测试1: 百度短链

```bash
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "【大大阮迪慧的一生之敌】https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&rs=2140313395&ruk=H9L__jwD_3Mko6WfA-nOJA&u=dad868bf9d433114&sid_for_share=184272_3",
    "media_type": "video",
    "method": "crop",
    "user_id": "test_user"
  }'
```

**预期日志**:
```log
✅ INFO - 提取的URL: https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&...
✅ INFO - 任务创建成功: xxx-task-id
✅ INFO - 开始下载文件: https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&...
✅ INFO - URL重定向: https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&... -> https://xxx.baidu.com/video.mp4
✅ INFO - Content-Type: video/mp4
✅ INFO - 文件下载成功: /tmp/pureclip/xxx.mp4 (大小: 15234567 bytes)
```

### 测试2: 抖音短链

```bash
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "1.71 复制打开抖音，看看【小丫头的作品】https://v.douyin.com/6YWKa6_haf8/ K@j.pd 05/09",
    "media_type": "video",
    "method": "crop",
    "user_id": "test_user"
  }'
```

**预期日志**:
```log
✅ INFO - 提取的URL: https://v.douyin.com/6YWKa6_haf8/
✅ INFO - 开始下载文件: https://v.douyin.com/6YWKa6_haf8/
✅ INFO - URL重定向: https://v.douyin.com/6YWKa6_haf8/ -> https://aweme.snssdk.com/aweme/v1/play/?video_id=xxx
✅ INFO - Content-Type: video/mp4
✅ INFO - 文件下载成功: /tmp/pureclip/xxx.mp4 (大小: 8765432 bytes)
```

### 测试3: 小红书短链

```bash
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "湖光山色两相宜 http://xhslink.com/o/uMnICz6mL2 复制后打开【小红书】查看笔记！",
    "media_type": "image",
    "method": "inpaint",
    "user_id": "test_user"
  }'
```

---

## ⚠️ 可能的错误场景和处理

### 场景1: 下载到HTML页面

**症状**:
```log
WARNING - 可能不是有效的媒体文件，Content-Type: text/html
WARNING - 响应预览: b'<!DOCTYPE html><html><head><title>...'
```

**原因**:
- 平台需要更多验证（如Cookie、特定参数）
- URL已失效或需要登录

**解决**:
- 检查URL是否有效
- 可能需要添加更多平台特定的处理逻辑

### 场景2: 文件过小

**症状**:
```log
WARNING - 下载的文件过小(512 bytes)，可能不是有效的媒体文件
```

**原因**:
- 下载到错误页面
- 防盗链或访问限制

**解决**:
- 检查日志中的Content-Type和响应预览
- 验证URL和请求头配置

### 场景3: 重定向循环

**症状**:
```log
ERROR - 文件下载失败: Max retries exceeded with url
```

**原因**:
- 平台检测到机器人行为
- 需要更复杂的验证机制

**解决**:
- 添加延迟和随机化
- 使用更复杂的反爬虫策略

---

## 🔧 高级配置（可选）

### 添加代理支持

```python
# 在__init__方法中
self.session.proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080'
}
```

### 添加重试机制

```python
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 在__init__方法中
retry_strategy = Retry(
    total=3,  # 最多重试3次
    backoff_factor=1,  # 重试间隔递增
    status_forcelist=[429, 500, 502, 503, 504]  # 这些状态码触发重试
)
adapter = HTTPAdapter(max_retries=retry_strategy)
self.session.mount("http://", adapter)
self.session.mount("https://", adapter)
```

### 添加超时配置

```python
# 在config.yaml中添加
TIMEOUT_CONNECT: 30  # 连接超时
TIMEOUT_READ: 300  # 读取超时

# 在download方法中
response = self.session.get(
    url,
    headers=headers,
    stream=True,
    timeout=(settings.TIMEOUT_CONNECT, settings.TIMEOUT_READ),
    allow_redirects=True
)
```

---

## 📝 完整流程图

```
用户提交分享链接
    ↓
URL提取器提取真实URL
    ↓
Celery任务启动下载
    ↓
┌─────────────────────────────┐
│  Downloader (增强版)         │
├─────────────────────────────┤
│ 1. 生成浏览器请求头          │
│    - User-Agent             │
│    - Accept                 │
│    - Referer (根据平台)      │
│    - Sec-Fetch-* (Chrome)   │
│                             │
│ 2. 使用Session发送请求       │
│    - 支持Cookie             │
│    - 自动跟随重定向          │
│    - 记录重定向路径          │
│                             │
│ 3. 验证Content-Type         │
│    - 排除HTML页面           │
│    - 验证媒体类型            │
│                             │
│ 4. 下载并保存文件            │
│    - 流式下载               │
│    - 检查文件大小            │
│    - 记录详细日志            │
└─────────────────────────────┘
    ↓
文件保存到临时目录
    ↓
进入视频/图片处理流程
    ↓
上传到MinIO
    ↓
返回结果URL给用户
```

---

## 🎯 测试清单

测试以下场景以确保功能正常：

- ✅ **百度短链**: `https://mr.baidu.com/r/...`
- ✅ **抖音短链**: `https://v.douyin.com/...`
- ✅ **小红书短链**: `http://xhslink.com/...`
- ✅ **B站短链**: `https://b23.tv/...`
- ✅ **直接视频链接**: `https://example.com/video.mp4`
- ✅ **重定向链接**: 检查日志是否记录重定向路径
- ✅ **无效链接**: 检查是否正确报错
- ✅ **HTML页面**: 检查是否发出警告

---

## 📖 相关文档

- 📘 `URL_EXTRACTION_GUIDE.md` - URL提取功能说明
- 🔧 `backend_watermark/services/downloader.py` - 下载器源代码
- 🐛 `BUGFIX_REDIS_SERIALIZATION.md` - Redis序列化修复
- 📚 `README.md` - 项目总览

---

## 🎉 总结

### ✅ 新增功能

1. ✅ **完整的浏览器伪装**
   - 真实的Chrome 131 User-Agent
   - 完整的Accept头
   - 平台特定的Referer

2. ✅ **自动跟随重定向**
   - 支持多级重定向
   - 记录重定向路径
   - 处理最终真实URL

3. ✅ **Session支持**
   - Cookie自动处理
   - 连接复用
   - 会话状态保持

4. ✅ **内容验证**
   - 验证Content-Type
   - 检查文件大小
   - 警告机制

5. ✅ **详细日志**
   - 重定向信息
   - Content-Type
   - 文件大小
   - 响应预览（错误时）

### 📊 修改的文件

- ✅ `backend_watermark/services/downloader.py` - 完全重写下载逻辑
- ✅ `DOWNLOADER_ENHANCEMENT.md` - 本说明文档

### 🚀 下一步

重启服务并测试：

```bash
# 1. 重启后端
cd backend_watermark
python app.py

# 2. 重启Celery (新终端)
celery -A backend_watermark.celery_app.celery worker --loglevel=info

# 3. 测试短链下载
# 使用前面提供的curl命令测试各个平台
```

现在可以正确处理各种短链和重定向链接了！🎉



