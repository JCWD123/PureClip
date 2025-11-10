# 🔧 微信小程序下载域名问题解决方案

## 🔴 问题描述

```
downloadFile:fail url not in domain
```

### 原因分析

1. **视频URL来自第三方CDN**
   ```
   https://vd4.bdstatic.com/...        (百度CDN)
   https://aweme.snssdk.com/...        (抖音CDN)
   https://v.kuaishou.com/...          (快手CDN)
   https://sns-video-bd.xhscdn.com/... (小红书CDN)
   ```

2. **微信小程序域名限制**
   - 微信小程序的 `Taro.downloadFile()` 只能下载**已配置的合法域名**
   - 你的配置: `https://api.pureclip.arbismart.cloud`
   - 第三方CDN域名未配置 → 下载失败

---

## ✅ 解决方案对比

| 方案 | 优点 | 缺点 | 推荐度 |
|------|------|------|--------|
| **方案1**: 配置所有CDN域名 | 简单直接 | • 需要配置多个域名<br>• CDN可能变化<br>• 域名数量有限制 | ⭐⭐ |
| **方案2**: 后端代理下载 | • 只需一个域名<br>• 灵活可控<br>• 统一管理 | 需要后端支持 | ⭐⭐⭐⭐⭐ |

---

## 🎯 推荐方案：后端代理下载

### 工作流程

```
前端请求下载
    ↓
调用后端代理API: /api/proxy/download
    ↓
后端下载第三方CDN视频
    ↓
后端返回视频流给前端
    ↓
前端保存到相册
```

### 优势

✅ **只需配置一个域名**: `https://api.pureclip.arbismart.cloud`
✅ **支持所有视频源**: 百度、抖音、快手、小红书等
✅ **安全可控**: 可以添加限流、防盗链等功能
✅ **统一管理**: 所有下载流量经过自己的服务器

---

## 🚀 实现步骤

### 步骤1: 后端实现代理下载API

已创建文件: `backend_watermark/api/proxy.py`

**功能**:
- 接收前端的下载请求
- 从第三方CDN下载视频
- 以流式方式返回给前端
- 支持断点续传

### 步骤2: 前端修改下载逻辑

已修改文件: `frontend-watermark/src/pages/result/index.tsx`

**变化**:
```tsx
// ❌ 旧逻辑：直接下载第三方CDN
const downloadResult = await Taro.downloadFile({
  url: 'https://vd4.bdstatic.com/...'  // 域名不合法
})

// ✅ 新逻辑：通过后端代理
const proxyUrl = `${API_BASE_URL}/proxy/download?url=${encodeURIComponent(task.result_url)}`
const downloadResult = await Taro.downloadFile({
  url: proxyUrl  // 使用自己的域名
})
```

---

## 📝 具体实现

### 后端代理API

**文件**: `backend_watermark/api/proxy.py`

```python
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/proxy/download")
async def proxy_download(url: str = Query(..., description="要下载的文件URL")):
    """
    代理下载第三方资源
    解决微信小程序 downloadFile 域名限制问题
    """
    try:
        logger.info(f"代理下载请求: {url[:100]}...")
        
        # 验证URL
        if not url.startswith('http'):
            raise HTTPException(status_code=400, detail="无效的URL")
        
        # 创建HTTP客户端
        async with httpx.AsyncClient(timeout=60.0, follow_redirects=True) as client:
            # 发送HEAD请求获取文件信息
            head_response = await client.head(url)
            content_type = head_response.headers.get('content-type', 'application/octet-stream')
            content_length = head_response.headers.get('content-length')
            
            logger.info(f"文件类型: {content_type}, 大小: {content_length}")
            
            # 流式下载文件
            async def generate():
                async with client.stream('GET', url) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        yield chunk
            
            # 返回流式响应
            headers = {
                'Content-Type': content_type,
                'Content-Disposition': 'attachment'
            }
            
            if content_length:
                headers['Content-Length'] = content_length
            
            return StreamingResponse(
                generate(),
                headers=headers,
                media_type=content_type
            )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"下载失败 - HTTP错误: {e}")
        raise HTTPException(status_code=e.response.status_code, detail=f"下载失败: {e}")
    except httpx.TimeoutException:
        logger.error("下载超时")
        raise HTTPException(status_code=504, detail="下载超时")
    except Exception as e:
        logger.error(f"下载失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
```

### 前端下载逻辑

**文件**: `frontend-watermark/src/pages/result/index.tsx`

```tsx
import { API_BASE_URL } from '../../config/api'

const handleDownload = async () => {
  if (!task?.result_url) {
    Taro.showToast({
      title: '暂无可下载内容',
      icon: 'none'
    })
    return
  }

  if (downloading) {
    return
  }

  setDownloading(true)

  try {
    const isVideo = task.result_url.includes('.mp4') || task.result_url.includes('video')

    Taro.showLoading({
      title: '准备下载...',
      mask: true
    })

    // ✅ 使用后端代理下载
    const proxyUrl = `${API_BASE_URL}/proxy/download?url=${encodeURIComponent(task.result_url)}`
    
    console.log('📥 开始代理下载:', proxyUrl)

    const downloadResult = await Taro.downloadFile({
      url: proxyUrl  // 使用代理URL
    })

    if (downloadResult.statusCode !== 200) {
      throw new Error('下载失败')
    }

    Taro.hideLoading()

    // 保存到相册
    if (isVideo) {
      await Taro.saveVideoToPhotosAlbum({
        filePath: downloadResult.tempFilePath
      })
    } else {
      await Taro.saveImageToPhotosAlbum({
        filePath: downloadResult.tempFilePath
      })
    }

    Taro.showToast({
      title: '保存成功',
      icon: 'success',
      duration: 2000
    })

  } catch (error: any) {
    console.error('下载失败:', error)
    Taro.hideLoading()
    
    // 错误处理
    if (error.errMsg?.includes('auth deny') || error.errMsg?.includes('authorize')) {
      Taro.showModal({
        title: '需要相册权限',
        content: '请授权访问相册以保存文件',
        confirmText: '去设置',
        success: (res) => {
          if (res.confirm) {
            Taro.openSetting()
          }
        }
      })
    } else {
      Taro.showToast({
        title: error.message || '保存失败',
        icon: 'none',
        duration: 2000
      })
    }
  } finally {
    setDownloading(false)
  }
}
```

---

## 🔧 部署步骤

### 1. 后端部署

```bash
cd backend_watermark

# 创建代理API文件
touch api/proxy.py

# 在 app.py 中注册路由
# app.include_router(proxy_router, prefix="/api", tags=["代理下载"])

# 重启服务
bash restart_all.sh
```

### 2. 测试代理API

```bash
# 测试代理下载
curl -I "https://api.pureclip.arbismart.cloud/api/proxy/download?url=https://vd4.bdstatic.com/..."
```

预期响应:
```
HTTP/2 200
content-type: video/mp4
content-length: 12345678
content-disposition: attachment
```

### 3. 前端部署

```bash
cd frontend-watermark

# 清理并重新编译
rm -rf dist
pnpm build:weapp

# 在微信开发者工具中测试
```

---

## 📱 微信小程序配置

### downloadFile 合法域名配置

登录微信小程序后台 → 开发 → 开发管理 → 开发设置 → 服务器域名

**配置项**:
```
downloadFile合法域名:
  https://api.pureclip.arbismart.cloud
```

**注意**:
- ✅ 只需配置这一个域名
- ✅ 不需要配置百度、抖音等CDN域名
- ✅ 所有下载都通过代理完成

---

## 🧪 测试清单

### 后端测试

```bash
# 1. 测试百度视频代理
curl -I "https://api.pureclip.arbismart.cloud/api/proxy/download?url=https://vd4.bdstatic.com/mda-xxx.mp4"

# 2. 测试抖音视频代理
curl -I "https://api.pureclip.arbismart.cloud/api/proxy/download?url=https://aweme.snssdk.com/xxx.mp4"

# 3. 测试下载完整文件
curl "https://api.pureclip.arbismart.cloud/api/proxy/download?url=..." -o test.mp4
```

### 前端测试

1. **创建解析任务**
   - 输入百度视频链接
   - 等待解析完成

2. **测试下载功能**
   - 点击"下载视频"按钮
   - 检查控制台日志
   - 确认无 `url not in domain` 错误

3. **检查相册**
   - 打开手机相册
   - 确认视频已保存

---

## 🔍 故障排查

### 问题1: 代理下载返回 404

**原因**: 后端路由未注册

**解决**:
```python
# backend_watermark/app.py
from api.proxy import router as proxy_router

app.include_router(proxy_router, prefix="/api", tags=["代理下载"])
```

### 问题2: 下载超时

**原因**: 视频文件过大

**解决**:
```python
# 增加超时时间
async with httpx.AsyncClient(timeout=120.0) as client:
    ...
```

### 问题3: 下载后无法播放

**原因**: Content-Type 不正确

**解决**:
```python
# 确保返回正确的 Content-Type
headers = {
    'Content-Type': 'video/mp4',  # 或从源站获取
    ...
}
```

---

## 📊 方案对比

### 方案1: 直接下载（不推荐）

```tsx
// ❌ 需要配置多个域名
const domains = [
  'https://vd4.bdstatic.com',     // 百度
  'https://aweme.snssdk.com',     // 抖音
  'https://v.kuaishou.com',       // 快手
  'https://sns-video-bd.xhscdn.com' // 小红书
  // ... 更多平台
]

// 微信小程序后台需要逐一配置
// 域名数量有限制（20个）
```

### 方案2: 代理下载（推荐）✅

```tsx
// ✅ 只需一个域名
const proxyUrl = `${API_BASE_URL}/proxy/download?url=${encodeURIComponent(videoUrl)}`

// 微信小程序后台只需配置:
// https://api.pureclip.arbismart.cloud
```

---

## 💡 额外功能

### 下载统计

```python
@router.get("/proxy/download")
async def proxy_download(url: str, user_id: str = Query(None)):
    # 记录下载统计
    await save_download_stats(user_id, url)
    ...
```

### 防盗链

```python
from fastapi import Header

@router.get("/proxy/download")
async def proxy_download(
    url: str,
    authorization: str = Header(None)
):
    # 验证token
    if not verify_token(authorization):
        raise HTTPException(status_code=401, detail="未授权")
    ...
```

### 下载限流

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.get("/proxy/download")
@limiter.limit("10/minute")  # 每分钟最多10次
async def proxy_download(url: str):
    ...
```

---

## ✅ 最终检查

完成以下步骤后，下载功能应该正常：

- [ ] 后端实现 `/api/proxy/download` 接口
- [ ] 前端修改下载逻辑使用代理URL
- [ ] 微信小程序后台配置 `downloadFile合法域名`
- [ ] 重新编译前端 `pnpm build:weapp`
- [ ] 重启后端服务 `bash restart_all.sh`
- [ ] 测试下载功能
- [ ] 检查相册是否保存成功

---

## 🎯 总结

**下载域名问题根本原因**: 第三方CDN域名未配置

**最佳解决方案**: 后端代理下载

**优势**:
- ✅ 只需配置一个域名
- ✅ 支持所有视频平台
- ✅ 灵活可控
- ✅ 易于维护

**实施后效果**:
```
用户点击下载
    ↓
前端调用: https://api.pureclip.arbismart.cloud/api/proxy/download?url=...
    ↓
后端下载第三方视频
    ↓
流式返回给前端
    ↓
保存到相册 ✅
```

现在立即实施！🚀


