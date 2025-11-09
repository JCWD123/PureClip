# Redis序列化问题修复说明

## 🐛 问题描述

在使用Redis缓存MongoDB数据时，出现两个序列化错误：

### 错误1: datetime对象无法序列化
```
Object of type datetime is not JSON serializable
```

### 错误2: ObjectId对象无法序列化
```
Type <class 'bson.objectid.ObjectId'> not serializable
```

## 🔍 根本原因

1. **datetime问题**: MongoDB存储的 `created_at`、`updated_at` 字段是Python的 `datetime` 对象，`json.dumps()` 无法直接序列化
2. **ObjectId问题**: MongoDB的 `_id` 字段是 `bson.objectid.ObjectId` 类型，也无法被JSON序列化

## ✅ 解决方案

### 1. 修复Redis客户端的序列化器

**文件**: `backend_watermark/core/redis_client.py`

```python
# 添加导入
from datetime import datetime
from bson import ObjectId

class RedisClient:
    def set(self, key: str, value: Any, expire: int = None):
        """设置缓存"""
        if self.client is None:
            self.connect()
        try:
            # 使用自定义序列化器处理特殊类型
            serialized_value = json.dumps(value, default=self._json_serializer)
            self.client.set(key, serialized_value, ex=expire)
        except Exception as e:
            logger.error(f"Redis设置失败: {e}")
    
    @staticmethod
    def _json_serializer(obj):
        """JSON序列化器，处理datetime和ObjectId对象"""
        if isinstance(obj, datetime):
            return obj.isoformat()  # 转为ISO格式字符串
        if isinstance(obj, ObjectId):
            return str(obj)  # 转为字符串
        raise TypeError(f"Type {type(obj)} not serializable")
```

### 2. 优化API层的缓存逻辑

**文件**: `backend_watermark/api/task.py`

```python
# 在创建任务时，排除_id字段
result = collection.insert_one(task_data)

# 缓存到Redis（排除MongoDB的_id）
cache_data = {k: v for k, v in task_data.items() if k != '_id'}
redis.set(f"task:{task_id}", cache_data, expire=3600 * 24)
```

### 3. 确保所有MongoDB查询都排除_id

**文件**: `backend_watermark/celery_app/tasks.py`

```python
# 更新Redis缓存（排除_id字段）
task = collection.find_one({"task_id": task_id}, {"_id": 0})
if task:
    redis.set(f"task:{task_id}", task, expire=3600 * 24)
```

## 📊 修复效果

### 修复前
```
❌ Redis设置失败: Object of type datetime is not JSON serializable
❌ Redis设置失败: Type <class 'bson.objectid.ObjectId'> not serializable
```

### 修复后
```
✅ 任务创建成功: xxx-task-id
✅ Redis缓存成功
✅ 任务状态更新成功
```

## 🔄 数据转换示例

### datetime对象
```python
# 原始值
created_at = datetime.now()  # datetime(2025, 11, 8, 15, 2, 42)

# 序列化后
"created_at": "2025-11-08T15:02:42.474000"
```

### ObjectId对象
```python
# 原始值
_id = ObjectId("6733a2e2f1234567890abcde")

# 序列化后
"_id": "6733a2e2f1234567890abcde"

# 更好的做法：直接排除_id字段
# MongoDB查询时使用 {"_id": 0}
```

## 🎯 最佳实践

### 1. MongoDB查询时排除_id
```python
# ✅ 好的做法
task = collection.find_one({"task_id": task_id}, {"_id": 0})

# ❌ 不好的做法
task = collection.find_one({"task_id": task_id})
```

### 2. 自定义JSON序列化器
```python
# ✅ 支持常见的不可序列化类型
def _json_serializer(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, bytes):
        return obj.decode('utf-8')
    raise TypeError(f"Type {type(obj)} not serializable")
```

### 3. 反序列化时的注意事项
```python
# datetime字符串需要手动转换回datetime对象（如果需要的话）
task_data = redis.get(f"task:{task_id}")
if task_data and "created_at" in task_data:
    from dateutil import parser
    task_data["created_at"] = parser.parse(task_data["created_at"])
```

## 📝 相关文件修改清单

- ✅ `backend_watermark/core/redis_client.py` - 添加自定义序列化器
- ✅ `backend_watermark/api/task.py` - 排除_id字段
- ✅ `backend_watermark/celery_app/tasks.py` - 优化缓存更新

## 🧪 测试验证

```bash
# 1. 重启后端服务
cd backend_watermark
python app.py

# 2. 重启Celery Worker
celery -A backend_watermark.celery_app.celery worker --loglevel=info

# 3. 提交测试任务
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/video.mp4",
    "media_type": "video",
    "method": "crop"
  }'

# 4. 查看日志，应该看到：
# ✅ 任务创建成功
# ✅ 无Redis序列化错误
# ✅ 任务状态正常更新
```

## 🎉 总结

通过添加自定义JSON序列化器和优化MongoDB查询，完全解决了Redis缓存时的序列化问题。系统现在可以正确缓存包含datetime和ObjectId字段的任务数据。

---

**修复日期**: 2025-11-08  
**影响范围**: Redis缓存模块  
**向后兼容**: 是


