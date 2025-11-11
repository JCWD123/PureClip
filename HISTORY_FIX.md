# 🔧 历史记录功能修复

## 🐛 问题描述

历史记录接口返回 500 错误：

```
2 validation errors for ProcessHistory
method
  Input should be 'crop', 'blur', 'cover' or 'inpaint' [type=enum, input_value='parse', input_type=str]
file_size
  Field required [type=missing]
```

### 原因分析

轻量级模式下：
- ❌ 保存的 `method` 是 `'parse'`（解析模式），但模型只允许 `crop/blur/cover/inpaint`
- ❌ 没有下载文件，所以 `file_size` 字段不存在，但模型要求必填

---

## ✅ 修复内容

### 1. 后端模型更新

**文件**: `backend_watermark/models/task.py`

#### 变更 1: 添加 `parse` 方法

```python
class WatermarkMethod(str, Enum):
    """去水印方法枚举"""
    CROP = "crop"
    BLUR = "blur"
    COVER = "cover"
    INPAINT = "inpaint"
    PARSE = "parse"  # ← 新增：解析模式（轻量级）
```

#### 变更 2: 字段改为可选

```python
class ProcessHistory(BaseModel):
    # ... 其他字段
    file_size: Optional[int] = Field(None, description="文件大小（字节）- 轻量级模式下为空")
    metadata: Optional[Dict[str, Any]] = Field(None, description="视频元数据（标题、作者等）")
    # ← file_size 改为可选，添加 metadata 字段
```

### 2. 前端历史页面更新

**文件**: `frontend-watermark/src/pages/history/index.tsx`

#### 变更 1: 添加 `parse` 方法文本

```tsx
const getMethodText = (method: string) => {
  const methodMap: Record<string, string> = {
    crop: '裁剪',
    blur: '模糊',
    cover: '覆盖',
    inpaint: '填充',
    parse: '链接解析'  // ← 新增
  }
  return methodMap[method] || method
}
```

#### 变更 2: 处理空文件大小

```tsx
const formatFileSize = (bytes?: number) => {
  if (!bytes) return '无需下载'  // ← 轻量级模式下显示
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
}
```

#### 变更 3: 显示视频元数据

```tsx
<View className='item-info'>
  {/* 新增：显示标题 */}
  {item.metadata?.title && (
    <View className='info-row'>
      <View className='info-label'>标题：</View>
      <View className='info-value'>{item.metadata.title}</View>
    </View>
  )}
  
  {/* 新增：显示作者 */}
  {item.metadata?.author && (
    <View className='info-row'>
      <View className='info-label'>作者：</View>
      <View className='info-value'>{item.metadata.author}</View>
    </View>
  )}
  
  {/* 新增：显示平台 */}
  {item.metadata?.platform && (
    <View className='info-row'>
      <View className='info-label'>平台：</View>
      <View className='info-value'>{item.metadata.platform}</View>
    </View>
  )}
  
  {/* 处理时间 */}
  <View className='info-row'>...</View>
  
  {/* 文件大小（如果存在） */}
  {item.file_size && (
    <View className='info-row'>
      <View className='info-label'>文件大小：</View>
      <View className='info-value'>{formatFileSize(item.file_size)}</View>
    </View>
  )}
  
  {/* 耗时 */}
  <View className='info-row'>...</View>
</View>
```

---

## 🚀 部署步骤

### 步骤1: 重启后端服务

```bash
cd /root/PureClip/backend_watermark

# 使用一键重启脚本
bash restart_all.sh
```

**预期输出**:
```
✅ Celery Worker 已在后台启动
✅ FastAPI 已在后台启动
✅ 重启完成！
```

### 步骤2: 更新前端（可选）

```bash
cd frontend-watermark

# 重新编译
npm run build:weapp

# 用微信开发者工具上传
```

---

## 🧪 测试验证

### 测试1: 提交新任务

```bash
curl -X POST https://api.pureclip.arbismart.cloud/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://v.douyin.com/6YWKa6_haf8/",
    "media_type": "video",
    "method": "crop",
    "user_id": "test_user_001"
  }'
```

### 测试2: 查询历史记录

```bash
curl "https://api.pureclip.arbismart.cloud/api/history?user_id=test_user_001&limit=10"
```

**预期响应**:
```json
{
  "total": 2,
  "history": [
    {
      "history_id": "xxx",
      "user_id": "test_user_001",
      "task_id": "xxx",
      "original_url": "【大大阮迪慧的一生之敌】https://mr.baidu.com/...",
      "result_url": "https://vd4.bdstatic.com/mda-rk5i6p94efaa9t6t/...",
      "media_type": "video",
      "method": "parse",  // ← 轻量级模式
      "process_time": 2.5,
      "file_size": null,  // ← 无文件大小
      "metadata": {       // ← 包含元数据
        "title": "大大阮迪慧的一生之敌",
        "author": "用户名",
        "platform": "baidu"
      },
      "created_at": "2025-11-09T15:30:00"
    }
  ]
}
```

### 测试3: 在小程序中查看历史

1. 打开小程序
2. 进入"历史记录"页面
3. 应该能看到：
   - ✅ 方法标签显示"链接解析"
   - ✅ 显示视频标题、作者、平台
   - ✅ 不显示文件大小（或显示"无需下载"）
   - ✅ 显示处理耗时（2-5秒）

---

## 📊 历史记录显示对比

### ❌ 修复前（旧架构）

```
🎬 视频           [裁剪]

处理时间：2025-11-09 15:30
文件大小：156.32 MB
耗时：290.50秒

[复制链接] [删除]
```

### ✅ 修复后（新架构）

```
🎬 视频           [链接解析]

标题：大大阮迪慧的一生之敌
作者：xxx
平台：baidu
处理时间：2025-11-09 15:30
耗时：2.50秒

[复制链接] [删除]
```

**特点**：
- ✅ 显示更多有用信息（标题、作者、平台）
- ✅ 不显示无用信息（文件大小）
- ✅ 耗时更短（2.5秒 vs 290秒）

---

## 🔍 故障排查

### 问题1: 仍然返回 500 错误

```bash
# 1. 确认服务已重启
ps aux | grep "uvicorn backend_watermark.app:app" | grep -v grep
ps aux | grep "celery -A backend_watermark.celery_app.celery" | grep -v grep

# 2. 查看日志
tail -f /tmp/pureclip_backend.log
tail -f /tmp/pureclip_celery.log

# 3. 强制重启
cd /root/PureClip/backend_watermark
bash stop_services.sh
sleep 3
bash restart_all.sh
```

### 问题2: 前端仍显示错误

```bash
# 1. 清除小程序缓存
# 微信开发者工具 > 清除缓存 > 重新编译

# 2. 重新编译前端
cd frontend-watermark
rm -rf dist
npm run build:weapp
```

### 问题3: 旧的历史记录仍然报错

旧的历史记录可能不符合新模型，有两个选择：

#### 选择1: 清空旧历史记录

```bash
# 进入 MongoDB
mongosh

# 使用数据库
use watermark

# 删除旧历史记录
db.process_history.deleteMany({ method: { $ne: "parse" } })

# 或者删除所有
db.process_history.deleteMany({})
```

#### 选择2: 更新旧历史记录

```bash
# 进入 MongoDB
mongosh

# 使用数据库
use watermark

# 添加默认 file_size 为 0
db.process_history.updateMany(
  { file_size: { $exists: false } },
  { $set: { file_size: 0 } }
)
```

---

## ✅ 验证清单

修复完成后，确认：

- [ ] 后端服务正常运行
- [ ] 提交新任务成功
- [ ] 查询历史记录不报错（状态码 200）
- [ ] 历史记录中包含 `method: "parse"`
- [ ] 历史记录中包含 `metadata` 字段
- [ ] 小程序历史页面正常显示
- [ ] 显示视频标题、作者、平台
- [ ] 不显示文件大小或显示"无需下载"

---

## 🎉 总结

### 修复的根本原因

轻量级模式改变了数据结构：
- **旧模式**: 下载文件 → 有 `file_size`，`method` 是处理方法
- **新模式**: 解析链接 → 无 `file_size`，`method` 是 `parse`

### 修复方案

1. ✅ 扩展 `WatermarkMethod` 枚举，支持 `parse`
2. ✅ 将 `file_size` 改为可选字段
3. ✅ 添加 `metadata` 字段存储视频信息
4. ✅ 前端适配新字段，显示更丰富的信息

---

**现在重启服务即可修复！** 🚀

```bash
cd /root/PureClip/backend_watermark
bash restart_all.sh
```



