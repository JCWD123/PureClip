# 🚀 生产环境脚本使用指南

## 📋 脚本列表

### 1️⃣ 启动脚本

| 脚本名 | 功能 | 用法 |
|--------|------|------|
| `start_prod.sh` | 启动 FastAPI 后端 | `bash start_prod.sh` |
| `start_celery_prod.sh` | 启动 Celery Worker | `bash start_celery_prod.sh` |
| `restart_all.sh` | 一键重启所有服务 | `bash restart_all.sh` ⭐推荐 |

### 2️⃣ 停止脚本

| 脚本名 | 功能 | 用法 |
|--------|------|------|
| `stop_services.sh` | 停止所有服务 | `bash stop_services.sh` |

---

## 🎯 常用操作

### 启动所有服务（推荐）

```bash
cd /root/PureClip/backend_watermark
bash restart_all.sh
```

**特点**：
- ✅ 自动停止旧进程
- ✅ 按顺序启动 Celery 和 FastAPI
- ✅ 验证服务状态
- ✅ 显示日志路径

---

### 单独启动服务

#### 启动 FastAPI

```bash
cd /root/PureClip/backend_watermark
bash start_prod.sh
```

**配置**：
- 端口: 8001
- Workers: 2
- 日志: `/tmp/pureclip_backend.log`

#### 启动 Celery

```bash
cd /root/PureClip/backend_watermark
bash start_celery_prod.sh
```

**配置**：
- 并发数: 2
- 日志级别: info
- 日志: `/tmp/pureclip_celery.log`

---

### 停止所有服务

```bash
cd /root/PureClip/backend_watermark
bash stop_services.sh
```

**操作**：
- 优雅停止所有进程
- 如果进程未响应，强制停止
- 清理端口占用

---

## 📊 查看服务状态

### 检查进程

```bash
# 查看 FastAPI 进程
ps aux | grep "uvicorn backend_watermark.app:app" | grep -v grep

# 查看 Celery 进程
ps aux | grep "celery -A backend_watermark.celery_app.celery" | grep -v grep
```

### 查看日志

```bash
# FastAPI 实时日志
tail -f /tmp/pureclip_backend.log

# Celery 实时日志
tail -f /tmp/pureclip_celery.log

# 查看最近 50 行
tail -n 50 /tmp/pureclip_backend.log
tail -n 50 /tmp/pureclip_celery.log
```

---

## 🧪 测试服务

### 测试 FastAPI

```bash
# 测试健康检查
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

# 查询任务
curl http://localhost:8001/api/tasks/{task_id}
```

### 测试 Celery

```bash
# 查看 Celery 日志
tail -f /tmp/pureclip_celery.log

# 应该看到类似输出：
# [2025-11-09 12:00:00] 开始处理任务: abc123
# [2025-11-09 12:00:02] ✅ 解析成功！
# [2025-11-09 12:00:03] ✅ 任务处理完成
```

---

## ⚙️ 进程管理

### 手动停止进程

```bash
# 停止 FastAPI
pkill -f "uvicorn backend_watermark.app:app"

# 停止 Celery
pkill -f "celery -A backend_watermark.celery_app.celery worker"

# 强制停止（如果上面的命令无效）
pkill -9 -f "uvicorn backend_watermark.app:app"
pkill -9 -f "celery -A backend_watermark.celery_app.celery worker"
```

### 清理端口占用

```bash
# 查看端口占用
lsof -i:8001

# 释放端口
lsof -ti:8001 | xargs kill -9
```

---

## 🔧 脚本特点

### 避免进程名冲突

脚本使用**完整的进程命令**来识别和停止进程：

```bash
# ✅ 精确匹配
pkill -f "uvicorn backend_watermark.app:app"
pkill -f "celery -A backend_watermark.celery_app.celery worker"

# ❌ 不会误杀其他应用
# 即使其他应用也叫 app.py 或 celery，也不会受影响
```

### 日志文件独立

```
/tmp/pureclip_backend.log  ← FastAPI 日志
/tmp/pureclip_celery.log   ← Celery 日志
```

不会与其他应用的日志冲突。

---

## 📖 使用示例

### 场景1: 首次部署

```bash
# 1. 进入项目目录
cd /root/PureClip/backend_watermark

# 2. 赋予执行权限
chmod +x *.sh

# 3. 启动所有服务
bash restart_all.sh
```

### 场景2: 代码更新后重启

```bash
# 1. 拉取最新代码
cd /root/PureClip
git pull

# 2. 重启服务
cd backend_watermark
bash restart_all.sh
```

### 场景3: 仅更新 Celery 任务逻辑

```bash
# 1. 只重启 Celery
cd /root/PureClip/backend_watermark
pkill -f "celery -A backend_watermark.celery_app.celery worker"
bash start_celery_prod.sh
```

### 场景4: 排查问题

```bash
# 1. 停止所有服务
bash stop_services.sh

# 2. 清空日志
> /tmp/pureclip_backend.log
> /tmp/pureclip_celery.log

# 3. 重新启动
bash restart_all.sh

# 4. 实时查看日志
tail -f /tmp/pureclip_backend.log
# 或
tail -f /tmp/pureclip_celery.log
```

---

## ⚠️ 注意事项

### 1. 虚拟环境

确保在正确的虚拟环境中运行：

```bash
conda activate PureClip
cd /root/PureClip/backend_watermark
bash restart_all.sh
```

### 2. 权限问题

如果遇到权限问题：

```bash
chmod +x *.sh
```

### 3. 端口占用

如果 8001 端口被其他程序占用：

```bash
# 查看占用
lsof -i:8001

# 修改端口（编辑 start_prod.sh）
--port 8002  # 改成其他端口
```

### 4. Redis/MongoDB 必须运行

确保依赖服务正常：

```bash
# 检查 Redis
redis-cli ping

# 检查 MongoDB
mongosh --eval "db.adminCommand('ping')"

# 检查 MinIO（如果使用）
curl http://localhost:9000/minio/health/live
```

---

## 🎉 总结

### 常用命令速查

```bash
# 一键重启（最常用）⭐
bash restart_all.sh

# 停止所有服务
bash stop_services.sh

# 查看日志
tail -f /tmp/pureclip_backend.log
tail -f /tmp/pureclip_celery.log

# 检查状态
ps aux | grep "uvicorn backend_watermark.app:app" | grep -v grep
ps aux | grep "celery -A backend_watermark.celery_app.celery" | grep -v grep
```

---

**推荐使用 `restart_all.sh` 一键重启所有服务！🚀**


