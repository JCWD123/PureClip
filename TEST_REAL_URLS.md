# 真实URL测试案例

本文档包含来自各大平台的真实分享链接，用于测试URL提取功能。

## 📱 测试案例

### 1. 抖音（Douyin）

**原始复制内容**:
```
1.71 复制打开抖音，看看【小丫头的作品】# # 全民猜歌达人 # 王家驹经典歌曲 # 前奏... https://v.douyin.com/6YWKa6_haf8/ K@j.pd 05/09 Atr:/
```

**提取的URL**:
```
https://v.douyin.com/6YWKa6_haf8/
```

**平台检测**: `douyin`

**API测试**:
```bash
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "1.71 复制打开抖音，看看【小丫头的作品】# # 全民猜歌达人 # 王家驹经典歌曲 # 前奏... https://v.douyin.com/6YWKa6_haf8/ K@j.pd 05/09 Atr:/",
    "media_type": "video",
    "method": "crop",
    "user_id": "test_user"
  }'
```

---

### 2. 百度（Baidu）

**原始复制内容**:
```
【大大阮迪慧的一生之敌】https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&rs=2140313395&ruk=H9L__jwD_3Mko6WfA-nOJA&u=dad868bf9d433114&sid_for_share=184272_3
```

**提取的URL**:
```
https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&rs=2140313395&ruk=H9L__jwD_3Mko6WfA-nOJA&u=dad868bf9d433114&sid_for_share=184272_3
```

**平台检测**: `baidu`

**API测试**:
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

---

### 3. 小红书（Xiaohongshu）

**原始复制内容**:
```
湖光山色两相宜 http://xhslink.com/o/uMnICz6mL2 

复制后打开【小红书】查看笔记！
```

**提取的URL**:
```
http://xhslink.com/o/uMnICz6mL2
```

**平台检测**: `xiaohongshu`

**API测试**:
```bash
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "湖光山色两相宜 http://xhslink.com/o/uMnICz6mL2 \n\n复制后打开【小红书】查看笔记！",
    "media_type": "image",
    "method": "crop",
    "user_id": "test_user"
  }'
```

---

## 🧪 批量测试脚本

### Python测试脚本

```python
import requests
import json

# 测试案例
test_cases = [
    {
        "name": "抖音分享",
        "input": "1.71 复制打开抖音，看看【小丫头的作品】# # 全民猜歌达人 # 王家驹经典歌曲 # 前奏... https://v.douyin.com/6YWKa6_haf8/ K@j.pd 05/09 Atr:/",
        "media_type": "video",
        "expected_url": "https://v.douyin.com/6YWKa6_haf8/"
    },
    {
        "name": "百度分享",
        "input": "【大大阮迪慧的一生之敌】https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&rs=2140313395&ruk=H9L__jwD_3Mko6WfA-nOJA&u=dad868bf9d433114&sid_for_share=184272_3",
        "media_type": "video",
        "expected_url": "https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&rs=2140313395&ruk=H9L__jwD_3Mko6WfA-nOJA&u=dad868bf9d433114&sid_for_share=184272_3"
    },
    {
        "name": "小红书分享",
        "input": "湖光山色两相宜 http://xhslink.com/o/uMnICz6mL2 \n\n复制后打开【小红书】查看笔记！",
        "media_type": "image",
        "expected_url": "http://xhslink.com/o/uMnICz6mL2"
    }
]

# API端点
API_URL = "http://localhost:8001/api/tasks"

print("=" * 80)
print("真实URL提取测试")
print("=" * 80)

for i, test in enumerate(test_cases, 1):
    print(f"\n测试 {i}: {test['name']}")
    print("-" * 80)
    print(f"输入文本: {test['input'][:80]}...")
    print(f"期望URL: {test['expected_url']}")
    
    try:
        response = requests.post(
            API_URL,
            json={
                "url": test['input'],
                "media_type": test['media_type'],
                "method": "crop",
                "user_id": "test_user"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 测试通过")
            print(f"任务ID: {data.get('task_id')}")
            print(f"状态: {data.get('status')}")
        else:
            print(f"❌ 测试失败")
            print(f"状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
    
    except Exception as e:
        print(f"❌ 测试异常: {e}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
```

### 运行测试

```bash
# 1. 确保后端服务已启动
cd backend_watermark
python app.py

# 2. 新终端运行Celery
celery -A backend_watermark.celery_app.celery worker --loglevel=info

# 3. 新终端运行测试
python test_real_urls.py
```

---

## 📊 测试结果示例

### 预期日志输出

```log
2025-11-08 16:00:00,000 - INFO - 提取的URL: https://v.douyin.com/6YWKa6_haf8/
2025-11-08 16:00:00,100 - INFO - 平台检测: douyin
2025-11-08 16:00:00,200 - INFO - 任务创建成功: xxx-task-id-1

2025-11-08 16:00:01,000 - INFO - 提取的URL: https://mr.baidu.com/r/1Mf25TiaqXu?f=cp&rs=2140313395&ruk=H9L__jwD_3Mko6WfA-nOJA&u=dad868bf9d433114&sid_for_share=184272_3
2025-11-08 16:00:01,100 - INFO - 平台检测: baidu
2025-11-08 16:00:01,200 - INFO - 任务创建成功: xxx-task-id-2

2025-11-08 16:00:02,000 - INFO - 提取的URL: http://xhslink.com/o/uMnICz6mL2
2025-11-08 16:00:02,100 - INFO - 平台检测: xiaohongshu
2025-11-08 16:00:02,200 - INFO - 任务创建成功: xxx-task-id-3
```

---

## 🎯 特殊字符处理

这些真实案例包含了各种特殊情况：

### 抖音链接特点
- ✅ 包含多个`#`符号
- ✅ 包含表情符号和特殊字符 `K@j.pd`
- ✅ 包含日期 `05/09`
- ✅ URL后还有其他内容 `Atr:/`

### 百度链接特点
- ✅ 带中文方括号 `【】`
- ✅ 复杂的查询参数（多个`&`和`=`）
- ✅ 下划线和连字符混合

### 小红书链接特点
- ✅ 使用HTTP（而非HTTPS）
- ✅ 包含换行符 `\n`
- ✅ 中文提示文字
- ✅ 短链接格式 `xhslink.com/o/`

---

## ✅ 验证清单

测试时请确认：

- [ ] URL能够正确提取
- [ ] 平台能够正确识别
- [ ] 任务能够成功创建
- [ ] 日志记录完整
- [ ] 错误处理正常
- [ ] 原始输入被保存（用于调试）

---

## 📝 注意事项

1. **链接时效性**: 这些分享链接可能会过期，建议使用时效性较长的测试链接
2. **权限问题**: 某些平台链接可能需要登录才能访问
3. **下载限制**: 某些平台可能有防爬虫机制，需要添加headers
4. **跳转处理**: 短链接可能需要处理302跳转

---

**测试日期**: 2025-11-08  
**更新说明**: 添加抖音、百度、小红书三个平台的真实测试案例



