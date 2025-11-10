# 🔧 启动脚本路径修复

## 🐛 问题

```
ModuleNotFoundError: No module named 'backend_watermark'
```

### 原因分析

启动脚本在 `backend_watermark/` 目录下运行，但 Python 模块导入需要从项目根目录（`PureClip/`）运行。

```bash
# ❌ 错误的目录结构
/home/admin/projects/PureClip/backend_watermark/ (当前目录)
└── 运行: uvicorn backend_watermark.app:app
    └── Python找不到 backend_watermark 模块

# ✅ 正确的目录结构
/home/admin/projects/PureClip/ (项目根目录)
├── backend_watermark/
│   └── app.py
└── 运行: uvicorn backend_watermark.app:app
    └── Python可以找到 backend_watermark 模块
```

---

## ✅ 修复内容

### 修改的脚本

1. ✅ `backend_watermark/start_prod.sh` - 自动切换到项目根目录
2. ✅ `backend_watermark/start_celery_prod.sh` - 自动切换到项目根目录
3. ✅ `backend_watermark/restart_all.sh` - 确保在正确目录
4. ✅ `backend_watermark/stop_services.sh` - 更新路径变量

### 关键修复代码

```bash
# 自动找到项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"  # 脚本所在目录
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"      # 上一级目录（项目根）
cd "$PROJECT_ROOT"                            # 切换到根目录

echo "📂 项目根目录: $(pwd)"
```

**工作原理**：
- 脚本在 `/path/to/PureClip/backend_watermark/start_prod.sh`
- `SCRIPT_DIR` = `/path/to/PureClip/backend_watermark`
- `PROJECT_ROOT` = `/path/to/PureClip`
- 切换到 `PureClip/` 目录后运行命令

---

## 🚀 现在可以正常启动了

### 方法1: 一键重启（推荐）

```bash
cd /home/admin/projects/PureClip/backend_watermark
bash restart_all.sh
```

**预期输出**：
```
✅ Celery Worker 已在后台启动
✅ FastAPI 已在后台启动
✅ 重启完成！
```

### 方法2: 单独启动

```bash
cd /home/admin/projects/PureClip/backend_watermark

# 启动 Celery
bash start_celery_prod.sh

# 启动 FastAPI
bash start_prod.sh
```

---

## 📊 目录结构说明

```
/home/admin/projects/PureClip/              ← 项目根目录（运行命令的位置）
├── backend_watermark/                       ← Python包
│   ├── __init__.py
│   ├── app.py                              ← FastAPI应用
│   ├── celery_app/
│   │   ├── __init__.py
│   │   ├── celery.py
│   │   └── tasks.py
│   ├── config/
│   ├── api/
│   ├── services/
│   ├── models/
│   │
│   ├── start_prod.sh                       ← 启动脚本（修复后）
│   ├── start_celery_prod.sh
│   ├── restart_all.sh
│   └── stop_services.sh
│
├── frontend-watermark/
└── README.md
```

### Python模块导入

从项目根目录运行时：
```python
# ✅ 可以正常导入
from backend_watermark.app import app
from backend_watermark.celery_app.celery import celery_app
from backend_watermark.config.config import settings
```

从 `backend_watermark/` 目录运行时：
```python
# ❌ 找不到模块
from backend_watermark.app import app  # ModuleNotFoundError
```

---

## 🧪 验证修复

### 步骤1: 重启服务

```bash
cd /home/admin/projects/PureClip/backend_watermark
bash restart_all.sh
```

### 步骤2: 检查日志

```bash
# Celery 日志
tail -f /tmp/pureclip_celery.log

# 应该看到类似输出：
# [2025-11-09 16:00:00] celery@hostname ready.
# [2025-11-09 16:00:00] Received task: process_watermark_task

# FastAPI 日志
tail -f /tmp/pureclip_backend.log

# 应该看到类似输出：
# INFO:     Started server process [12345]
# INFO:     Waiting for application startup.
# INFO:     Application startup complete.
# INFO:     Uvicorn running on http://0.0.0.0:8001
```

### 步骤3: 测试服务

```bash
# 测试 API
curl http://localhost:8001/docs

# 提交任务
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://v.douyin.com/6YWKa6_haf8/",
    "media_type": "video",
    "method": "crop",
    "user_id": "test"
  }'
```

---

## 🔍 故障排查

### 问题1: 仍然提示模块未找到

```bash
# 检查当前目录
pwd
# 应该显示: /home/admin/projects/PureClip

# 检查 backend_watermark 目录是否存在
ls -la backend_watermark/
# 应该能看到 __init__.py, app.py 等文件

# 检查 Python 路径
python -c "import sys; print('\n'.join(sys.path))"
# 应该包含当前目录
```

### 问题2: 权限错误

```bash
# 赋予脚本执行权限
chmod +x backend_watermark/*.sh
```

### 问题3: 虚拟环境未激活

```bash
# 激活虚拟环境
conda activate PureClip

# 检查虚拟环境
which python
# 应该显示: /home/admin/miniconda3/envs/PureClip/bin/python
```

### 问题4: 依赖包缺失

```bash
# 重新安装依赖
cd /home/admin/projects/PureClip
pip install -r backend_watermark/requirements.txt
```

---

## 📝 手动启动方式（备用）

如果脚本仍有问题，可以手动启动：

### 手动启动 Celery

```bash
cd /home/admin/projects/PureClip
conda activate PureClip

nohup celery -A backend_watermark.celery_app.celery worker \
    --loglevel=info \
    --concurrency=2 \
    > /tmp/pureclip_celery.log 2>&1 &

echo $!  # 显示进程ID
```

### 手动启动 FastAPI

```bash
cd /home/admin/projects/PureClip
conda activate PureClip

nohup uvicorn backend_watermark.app:app \
    --host 0.0.0.0 \
    --port 8001 \
    --workers 2 \
    > /tmp/pureclip_backend.log 2>&1 &

echo $!  # 显示进程ID
```

---

## ✅ 验证清单

修复后确认：

- [ ] 脚本自动切换到项目根目录
- [ ] Celery 启动成功（无模块错误）
- [ ] FastAPI 启动成功（无模块错误）
- [ ] 日志文件正常记录
- [ ] API 可以正常访问
- [ ] 提交任务成功
- [ ] Celery 能处理任务

---

## 🎉 总结

### 问题根源
- ❌ 在 `backend_watermark/` 目录运行脚本
- ❌ Python 找不到 `backend_watermark` 模块

### 解决方案
- ✅ 脚本自动切换到项目根目录（`PureClip/`）
- ✅ Python 能正确导入模块

### 测试结果
```bash
cd /home/admin/projects/PureClip/backend_watermark
bash restart_all.sh

# 预期输出:
✅ Celery Worker 已在后台启动
✅ FastAPI 已在后台启动
✅ 重启完成！
```

---

**现在重新运行启动脚本即可！** 🚀

```bash
cd /home/admin/projects/PureClip/backend_watermark
bash restart_all.sh
```

应该不会再有 `ModuleNotFoundError` 错误了！✨


