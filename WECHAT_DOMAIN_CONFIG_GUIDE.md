# 🔧 微信小程序域名配置完整指南

## 🔴 问题现象

### 错误信息
```
downloadFile:fail url not in domain list:api.pureclip.ar
```

### 现象对比
| 环境 | 下载功能 | 原因 |
|------|---------|------|
| **开发者工具** | ✅ 正常 | 可以关闭域名校验 |
| **真机调试** | ✅ 正常 | 开发者账号跳过校验 |
| **审核版本** | ❌ 失败 | 严格校验域名配置 |
| **正式版本** | ❌ 失败 | 严格校验域名配置 |

---

## 🎯 根本原因

微信小程序对网络请求有严格的域名白名单限制：

1. **request 合法域名** - 用于 `wx.request()` / `Taro.request()`
2. **uploadFile 合法域名** - 用于 `wx.uploadFile()` / `Taro.uploadFile()`
3. **downloadFile 合法域名** - 用于 `wx.downloadFile()` / `Taro.downloadFile()` ⚠️
4. **socket 合法域名** - 用于 WebSocket

**你的问题**：`downloadFile合法域名` 未配置或配置错误！

---

## 📝 完整配置步骤

### 步骤1: 登录微信小程序后台

1. 访问：https://mp.weixin.qq.com
2. 使用管理员微信扫码登录
3. 选择你的小程序

---

### 步骤2: 进入域名配置页面

导航路径：
```
开发 → 开发管理 → 开发设置 → 服务器域名
```

或直接访问：
```
https://mp.weixin.qq.com/wxamp/devprofile/get_profile
```

---

### 步骤3: 配置所有必要的域名

#### 1. request 合法域名 ✅

**用途**: API 请求（创建任务、查询状态、历史记录等）

**需要配置**:
```
https://api.pureclip.arbismart.cloud
```

**对应前端代码**:
```tsx
// src/config/api.ts
export const API_BASE_URL = 'https://api.pureclip.arbismart.cloud/api'

// 用于这些请求:
await taskApi.createTask(...)  // POST /api/tasks
await taskApi.getTask(...)     // GET /api/tasks/{id}
await historyApi.getHistory(...) // GET /api/history
```

#### 2. downloadFile 合法域名 ⚠️ **关键！**

**用途**: 下载视频/图片到本地

**需要配置**:
```
https://api.pureclip.arbismart.cloud
```

**对应前端代码**:
```tsx
// src/pages/result/index.tsx
const proxyUrl = `${API_BASE_URL}/proxy/download?url=...`
await Taro.downloadFile({
  url: proxyUrl  // 必须在 downloadFile 合法域名中
})
```

**⚠️ 注意**:
- 必须是 **完整域名**，不能带路径
- ✅ 正确: `https://api.pureclip.arbismart.cloud`
- ❌ 错误: `https://api.pureclip.arbismart.cloud/api`
- ❌ 错误: `api.pureclip.arbismart.cloud` (缺少协议)

#### 3. uploadFile 合法域名（可选）

**用途**: 上传文件（如果有上传功能）

**需要配置**:
```
https://api.pureclip.arbismart.cloud
```

---

### 步骤4: 域名配置格式要求

#### ✅ 正确格式

```
https://api.pureclip.arbismart.cloud
```

#### ❌ 错误格式

```
# 错误1: 带路径
https://api.pureclip.arbismart.cloud/api  ❌

# 错误2: 带端口
https://api.pureclip.arbismart.cloud:443  ❌

# 错误3: 缺少协议
api.pureclip.arbismart.cloud  ❌

# 错误4: 使用 http（必须 https）
http://api.pureclip.arbismart.cloud  ❌

# 错误5: 通配符（不支持）
https://*.arbismart.cloud  ❌
```

---

### 步骤5: 域名要求

#### 必须满足的条件

1. ✅ **必须使用 HTTPS**（不能是 HTTP）
2. ✅ **必须备案**（中国大陆服务器）
3. ✅ **必须有效的 SSL 证书**
4. ✅ **不能使用 IP 地址**
5. ✅ **不能使用本地域名**（localhost, 127.0.0.1）

#### 验证域名配置

```bash
# 1. 检查域名可访问
curl -I https://api.pureclip.arbismart.cloud

# 预期响应:
# HTTP/2 200
# content-type: application/json

# 2. 检查 SSL 证书
openssl s_client -connect api.pureclip.arbismart.cloud:443 -servername api.pureclip.arbismart.cloud

# 3. 检查备案（中国大陆）
# 访问 https://beian.miit.gov.cn/
```

---

### 步骤6: 保存配置

1. 点击 **"开始配置"** 或 **"修改"**
2. 输入域名（一行一个）
3. 点击 **"保存并提交"**
4. **等待审核**（通常1-2小时，最长24小时）

⚠️ **重要**:
- 每月只能修改 **5次**
- 修改后需要重新提交代码审核
- 审核通过前，旧配置仍然生效

---

## 📱 完整配置清单

### PureClip 小程序需要配置的域名

```
服务器域名配置:

┌─────────────────────────────────────────────────────┐
│ 1. request 合法域名                                  │
│    https://api.pureclip.arbismart.cloud            │
│                                                     │
│ 2. uploadFile 合法域名（可选）                       │
│    https://api.pureclip.arbismart.cloud            │
│                                                     │
│ 3. downloadFile 合法域名 ⚠️ 必须配置                 │
│    https://api.pureclip.arbismart.cloud            │
│                                                     │
│ 4. socket 合法域名（可选，如无WebSocket可不配）      │
│    （无）                                           │
└─────────────────────────────────────────────────────┘
```

---

## 🔍 配置验证

### 方法1: 微信开发者工具

1. 打开小程序项目
2. 点击 **"详情"** → **"本地设置"**
3. **勾选** ✅ "不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书"
4. 取消勾选（恢复校验）
5. 测试下载功能
6. **预期**: 如果配置正确，下载应该成功

### 方法2: 真机预览

1. 在微信开发者工具点击 **"预览"**
2. 使用**非管理员**微信扫码
3. 测试下载功能
4. **预期**: 如果配置正确，下载应该成功

### 方法3: 体验版

1. 上传代码为 **体验版**
2. 在小程序后台添加体验成员
3. 体验成员扫码进入
4. 测试下载功能
5. **预期**: 如果配置正确，下载应该成功

---

## 🚨 常见错误及解决方案

### 错误1: url not in domain list

```
downloadFile:fail url not in domain list
```

**原因**: 域名未配置或配置错误

**解决方案**:
1. 检查微信后台 `downloadFile合法域名` 是否已配置
2. 确认域名格式正确（不带路径、端口）
3. 等待域名审核通过（1-2小时）

---

### 错误2: request:fail ssl hand shake error

```
request:fail ssl hand shake error
```

**原因**: SSL 证书问题

**解决方案**:
```bash
# 1. 检查证书有效性
curl -I https://api.pureclip.arbismart.cloud

# 2. 检查证书链
openssl s_client -connect api.pureclip.arbismart.cloud:443

# 3. 确保使用了完整的证书链
# 在 Nginx 配置中:
ssl_certificate /path/to/fullchain.pem;  # 使用 fullchain，不是 cert.pem
ssl_certificate_key /path/to/privkey.pem;
```

---

### 错误3: request:fail -202

```
request:fail -202:net::ERR_CERT_AUTHORITY_INVALID
```

**原因**: 证书不被信任

**解决方案**:
1. 使用正规 CA 颁发的证书（Let's Encrypt、阿里云等）
2. 不要使用自签名证书
3. 确保证书未过期

---

### 错误4: 修改域名后仍然报错

**原因**: 
1. 域名审核未通过
2. 未重新提交代码
3. 小程序缓存

**解决方案**:
1. 等待域名审核通过（查看审核状态）
2. 重新上传代码并提交审核
3. 在微信中删除小程序，重新搜索进入

---

### 错误5: 真机调试可用，正式版不可用

**原因**: 开发者账号跳过域名校验

**解决方案**:
1. 确保微信后台已配置域名
2. 使用**非管理员**账号测试体验版
3. 等待域名审核通过后再提交正式版

---

## 📊 配置检查清单

### 第1步：微信后台配置

- [ ] 登录微信小程序后台
- [ ] 进入 `开发 → 开发管理 → 开发设置 → 服务器域名`
- [ ] 配置 `request 合法域名`: `https://api.pureclip.arbismart.cloud`
- [ ] 配置 `downloadFile 合法域名`: `https://api.pureclip.arbismart.cloud` ⚠️
- [ ] 点击保存并提交
- [ ] 等待审核通过（1-2小时）

### 第2步：服务器配置

- [ ] 确保域名使用 HTTPS
- [ ] 确保 SSL 证书有效（未过期）
- [ ] 确保服务器正常响应
- [ ] 测试代理下载接口可用

```bash
# 测试 API 可访问性
curl -I https://api.pureclip.arbismart.cloud/api/proxy/download?url=test

# 预期: HTTP/2 200 或 400（参数错误，但能访问）
```

### 第3步：前端代码

- [ ] 确认 API_BASE_URL 使用的是正式域名
- [ ] 确认下载功能使用代理 URL

```tsx
// src/config/api.ts
export const API_BASE_URL = 'https://api.pureclip.arbismart.cloud/api'

// src/pages/result/index.tsx
const proxyUrl = `${API_BASE_URL}/proxy/download?url=...`
await Taro.downloadFile({ url: proxyUrl })
```

### 第4步：重新提交审核

- [ ] 清理本地编译文件 `rm -rf dist`
- [ ] 重新编译 `pnpm build:weapp`
- [ ] 在微信开发者工具中上传代码
- [ ] 填写版本说明
- [ ] 提交审核
- [ ] 等待审核通过（1-3天）

### 第5步：测试验证

- [ ] 体验版测试（非管理员账号）
- [ ] 确认下载功能正常
- [ ] 审核通过后，正式版测试

---

## 🎯 最佳实践

### 1. 域名规划

**统一使用一个域名**:
```
主域名: api.pureclip.arbismart.cloud

所有功能都通过这个域名:
- API 请求: https://api.pureclip.arbismart.cloud/api/*
- 代理下载: https://api.pureclip.arbismart.cloud/api/proxy/download
- 其他功能: https://api.pureclip.arbismart.cloud/api/*
```

**优势**:
- ✅ 只需配置一个域名
- ✅ 便于管理和维护
- ✅ 避免配置错误

### 2. 环境管理

```tsx
// src/config/api.ts
export const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? 'https://api.pureclip.arbismart.cloud/api'  // 生产环境
  : 'http://localhost:8001/api'  // 开发环境

// 开发时关闭域名校验
// 发布时使用生产域名
```

### 3. 错误处理

```tsx
const handleDownload = async () => {
  try {
    const proxyUrl = `${API_BASE_URL}/proxy/download?url=${encodeURIComponent(videoUrl)}`
    await Taro.downloadFile({ url: proxyUrl })
  } catch (error: any) {
    // 域名错误
    if (error.errMsg?.includes('domain')) {
      Taro.showModal({
        title: '下载失败',
        content: '网络配置错误，请联系客服',
        showCancel: false
      })
    }
    // 其他错误
    else {
      Taro.showToast({
        title: error.errMsg || '下载失败',
        icon: 'none'
      })
    }
  }
}
```

---

## 📖 微信官方文档

- [服务器域名配置](https://developers.weixin.qq.com/miniprogram/dev/framework/ability/network.html)
- [网络请求接口](https://developers.weixin.qq.com/miniprogram/dev/api/network/request/wx.request.html)
- [下载文件接口](https://developers.weixin.qq.com/miniprogram/dev/api/network/download/wx.downloadFile.html)

---

## 🎉 配置完成后

### 预期效果

1. **开发环境** ✅
   - 关闭域名校验，使用 localhost

2. **真机调试** ✅
   - 使用正式域名，管理员账号可跳过校验

3. **体验版** ✅
   - 严格校验域名，测试真实环境

4. **正式版** ✅
   - 严格校验域名，所有用户可用

### 成功标志

```
用户操作: 点击下载按钮
    ↓
前端调用: Taro.downloadFile({ url: proxyUrl })
    ↓
后端处理: 代理下载第三方视频
    ↓
返回数据: 流式返回给前端
    ↓
前端保存: saveVideoToPhotosAlbum
    ↓
✅ 成功: 视频保存到相册
```

---

## 🚀 立即行动

### 1. 配置域名

```
登录: https://mp.weixin.qq.com
路径: 开发 → 开发管理 → 开发设置 → 服务器域名

配置:
  request 合法域名: https://api.pureclip.arbismart.cloud
  downloadFile 合法域名: https://api.pureclip.arbismart.cloud

保存并提交
```

### 2. 等待审核

```
审核时间: 1-2小时（最长24小时）
审核状态: 在域名配置页面查看
```

### 3. 重新提交代码

```bash
cd frontend-watermark
rm -rf dist
pnpm build:weapp

# 微信开发者工具:
# 1. 上传代码
# 2. 填写版本说明: "修复下载功能，配置合法域名"
# 3. 提交审核
```

### 4. 测试验证

```
1. 体验版测试（非管理员账号）
2. 确认下载功能正常
3. 等待正式版审核通过
4. 正式版测试
```

---

**按照以上步骤操作，下载功能将在正式版中正常工作！** 🚀


