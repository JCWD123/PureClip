# URL提取功能使用指南

## 📋 功能说明

系统现在支持**智能URL提取**功能，可以从用户复制的各种文本中自动提取视频或图片URL。

### ✨ 支持的场景

1. **纯URL**
   ```
   https://example.com/video.mp4
   ```

2. **带文字的复制内容**
   ```
   观看这个精彩视频 https://example.com/video.mp4 非常好看！
   ```

3. **多个URL（提取第一个）**
   ```
   视频链接：https://example.com/video1.mp4 
   图片链接：https://example.com/image1.jpg
   # 将提取：https://example.com/video1.mp4
   ```

4. **常见分享链接**
   ```
   【抖音】复制此链接，打开抖音搜索，看Ta的作品 https://v.douyin.com/xxxx/
   ```

5. **包含中文的文本**
   ```
   这是我拍的视频https://example.com/myvideo.mp4大家看看
   ```

## 🔧 技术实现

### 1. URL提取函数

**文件**: `backend_watermark/utils/url_extractor.py`

```python
import re

def extract_url(text: str) -> Optional[str]:
    """
    从文本中智能提取URL
    
    特点：
    1. 支持http和https协议
    2. 自动过滤中文字符
    3. 清理末尾的标点符号
    4. 返回第一个有效URL
    """
    # 正则表达式：匹配http/https开头的URL
    url_pattern = r'https?://[^\s\u4e00-\u9fa5<>"{}|\\^`\[\]]+(?:[^\s\u4e00-\u9fa5<>"{}|\\^`\[\].,;!?])'
    urls = re.findall(url_pattern, text)
    
    if urls:
        # 清理URL末尾的标点符号
        url = urls[0].strip()
        while url and url[-1] in '.,;!?)]}、。，；！？」】':
            url = url[:-1]
        return url
    
    return None
```

### 2. API集成

**文件**: `backend_watermark/api/task.py`

```python
from backend_watermark.utils.url_extractor import extract_url, is_valid_url

@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    # 从输入文本中提取URL
    extracted_url = extract_url(task.url)
    
    if not extracted_url:
        raise HTTPException(status_code=400, detail="无法提取有效的URL")
    
    # 验证URL格式
    if not is_valid_url(extracted_url):
        raise HTTPException(status_code=400, detail="URL格式无效")
    
    # 使用提取后的URL创建任务
    task_data = {
        "url": extracted_url,
        "original_input": task.url,  # 保存原始输入用于调试
        ...
    }
```

## 📝 使用示例

### 示例1: 纯URL

**输入**:
```
https://www.w3schools.com/html/mov_bbb.mp4
```

**提取结果**:
```
https://www.w3schools.com/html/mov_bbb.mp4
```

### 示例2: 带文字的复制内容

**输入**:
```
分享一个视频给你看 https://example.com/video.mp4 超级好看的！
```

**提取结果**:
```
https://example.com/video.mp4
```

### 示例3: 抖音分享链接

**输入**:
```
【抖音】看看这个作品 https://v.douyin.com/iRNBho6/ 复制此链接，打开抖音App
```

**提取结果**:
```
https://v.douyin.com/iRNBho6/
```

### 示例4: 带标点符号

**输入**:
```
视频地址：https://example.com/video.mp4，请查收。
```

**提取结果**:
```
https://example.com/video.mp4
```
（自动去除末尾的逗号和句号）

### 示例5: 微信分享

**输入**:
```
这是微信的视频 https://mp.weixin.qq.com/s/xxxxxx 快来看
```

**提取结果**:
```
https://mp.weixin.qq.com/s/xxxxxx
```

## 🧪 API测试

### cURL测试

```bash
# 测试1: 纯URL
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://www.w3schools.com/html/mov_bbb.mp4",
    "media_type": "video",
    "method": "crop"
  }'

# 测试2: 带文字的复制内容
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "分享视频 https://example.com/video.mp4 很好看",
    "media_type": "video",
    "method": "crop"
  }'

# 测试3: 抖音链接
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "【抖音】https://v.douyin.com/xxxx/ 复制链接打开",
    "media_type": "video",
    "method": "crop"
  }'
```

### Python测试

```python
import requests

# 测试URL提取
test_cases = [
    "https://example.com/video.mp4",
    "观看视频 https://example.com/video.mp4 很精彩",
    "【抖音】https://v.douyin.com/xxxx/ 打开看看",
    "视频：https://example.com/video.mp4。",
]

for text in test_cases:
    response = requests.post(
        "http://localhost:8001/api/tasks",
        json={
            "url": text,
            "media_type": "video",
            "method": "crop",
            "user_id": "test_user"
        }
    )
    print(f"输入: {text}")
    print(f"结果: {response.json()}")
    print("-" * 50)
```

## 🎯 支持的视频平台

系统可以检测并支持以下平台的链接：

| 平台 | URL模式 | 示例 |
|------|---------|------|
| 抖音 | v.douyin.com | https://v.douyin.com/xxxx/ |
| 快手 | v.kuaishou.com | https://v.kuaishou.com/xxxx |
| B站 | bilibili.com, b23.tv | https://www.bilibili.com/video/BVxxxx |
| 微信 | mp.weixin.qq.com | https://mp.weixin.qq.com/s/xxxx |
| 小红书 | xhslink.com | http://xhslink.com/o/xxxx |
| 百度 | mr.baidu.com, pan.baidu.com | https://mr.baidu.com/r/xxxx |
| YouTube | youtube.com, youtu.be | https://www.youtube.com/watch?v=xxxx |
| TikTok | tiktok.com | https://www.tiktok.com/@user/video/xxxx |

## ⚠️ 注意事项

### 1. URL必须包含协议

❌ **错误**: `www.example.com/video.mp4`

✅ **正确**: `https://www.example.com/video.mp4`

### 2. 提取第一个URL

如果文本包含多个URL，系统将提取第一个：

```
输入: "视频1: https://url1.com 视频2: https://url2.com"
提取: https://url1.com
```

### 3. 无法提取的情况

以下情况会返回错误：

- 文本中不包含任何URL
- URL格式严重错误
- 没有http://或https://协议

```json
{
  "detail": "无法从输入文本中提取有效的URL，请确保包含完整的http://或https://链接"
}
```

## 🔍 调试信息

### 查看提取日志

启动后端服务后，可以在日志中查看URL提取过程：

```log
2025-11-08 15:20:00,000 - INFO - 提取的URL: https://example.com/video.mp4
2025-11-08 15:20:00,100 - INFO - 任务创建成功: xxx-task-id
```

### 查看原始输入

任务记录中保存了原始输入，可用于调试：

```json
{
  "task_id": "xxx",
  "url": "https://example.com/video.mp4",  // 提取后的URL
  "original_input": "观看视频 https://example.com/video.mp4 很好看"  // 原始输入
}
```

## 📊 工具函数API

### extract_url(text: str)

从文本中提取单个URL

**参数**:
- `text`: 输入文本

**返回**:
- 提取的URL字符串，失败返回None

### extract_all_urls(text: str)

从文本中提取所有URL

**参数**:
- `text`: 输入文本

**返回**:
- URL列表

### is_valid_url(url: str)

验证URL是否有效

**参数**:
- `url`: URL字符串

**返回**:
- True/False

### detect_platform(url: str)

检测URL所属的视频平台

**参数**:
- `url`: URL字符串

**返回**:
- 平台名称字符串，未识别返回None

## 🎉 优势

1. **用户体验好**: 用户可以直接粘贴复制的内容，不需要手动清理
2. **智能识别**: 自动过滤中文、标点符号等干扰内容
3. **兼容性强**: 支持各大视频平台的分享链接
4. **调试友好**: 保存原始输入便于问题排查

## 📖 相关文件

- `backend_watermark/utils/url_extractor.py` - URL提取核心逻辑
- `backend_watermark/api/task.py` - API集成
- `URL_EXTRACTION_GUIDE.md` - 本文档

---

**版本**: 1.0.0  
**更新时间**: 2025-11-08  
**作者**: PureClip Team

