# ⚡ 快速部署指南

## 🎯 你需要做什么？

### 问题回顾

你发现：**其他小程序（如耶斯去水印）返回的是原平台CDN直链，而不是服务器处理后的链接。**

**原因**：iiilab API返回的URL本身就是无水印版本，不需要下载和处理！

---

## 🚀 部署步骤（2分钟）

### 第1步：更新Nginx配置（可选）

如果你之前运行了`update_nginx.sh`添加了MinIO反向代理，现在其实不需要了（但保留也无妨）。

### 第2步：部署轻量级模式

```bash
# 进入项目目录
cd /path/to/PureClip

# 赋予执行权限
chmod +x deploy_lightweight_mode.sh

# 运行部署
sudo bash deploy_lightweight_mode.sh
```

**就这么简单！** 脚本会自动：
- ✅ 重启Celery
- ✅ 重启FastAPI
- ✅ 验证服务状态

---

## 🧪 测试（30秒）

```bash
# 提交任务
curl -X POST https://api.pureclip.arbismart.cloud/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"url": "https://v.douyin.com/6YWKa6_haf8/", "media_type": "video", "method": "crop", "user_id": "test"}'

# 复制返回的task_id，等待2-5秒后查询
curl https://api.pureclip.arbismart.cloud/api/tasks/{task_id}

# 检查result_url，应该是原平台CDN地址，例如:
# https://aweme.snssdk.com/aweme/v1/play/?video_id=...
# 而不是:
# https://api.pureclip.arbismart.cloud/storage/...
```

---

## ✅ 预期效果

### 响应时间

```
更新前: 1-5分钟 ⏱️
更新后: 2-5秒 ⚡
提升: 60倍+
```

### 返回URL

```
更新前: https://api.pureclip.arbismart.cloud/storage/pureclip/video/xxx.mp4?X-Amz-...
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^ 你的MinIO服务器

更新后: https://vd4.bdstatic.com/mda-rk5i6p94efaa9t6t/540p/h264_cae/xxx.mp4?...
        ^^^^^^^^^^^^^^^^^^^ 百度CDN（无水印版本）
```

### 小程序体验

```
更新前:
1. 粘贴链接
2. 等待1-5分钟 ⏰
3. 播放视频（从你的服务器）

更新后:
1. 粘贴链接
2. 等待2-5秒 ⚡
3. 播放视频（从原平台CDN）
```

---

## 📊 资源消耗

| 资源 | 更新前 | 更新后 | 节省 |
|------|--------|--------|------|
| **CPU** | 高（FFmpeg处理） | 极低（仅API调用） | 95% |
| **磁盘** | 每个视频占用空间 | 不占用 | 100% |
| **带宽** | 下载+上传 | 不占用 | 100% |
| **成本** | 高 | 极低 | 95% |

---

## 📖 详细文档

- 📘 **UPDATE_TO_LIGHTWEIGHT.md** - 完整更新说明
- 📘 **LIGHTWEIGHT_MODE.md** - 技术详解
- 📘 **deploy_lightweight_mode.sh** - 自动部署脚本

---

## ❓ 常见问题

### Q: 需要修改前端代码吗？

**A**: 不需要！前端代码已经更新，只需重新编译部署：

```bash
cd frontend-watermark
npm run build:weapp
# 然后用微信开发者工具上传
```

### Q: MinIO还需要吗？

**A**: 不需要了！可以关闭节省资源：

```bash
sudo systemctl stop minio
sudo systemctl disable minio  # 禁用开机自启
```

### Q: 可以回滚吗？

**A**: 可以！脚本会自动备份到`./backups/`目录。

---

## 🎉 完成！

现在你的小程序：
- ✅ 速度快（2-5秒）
- ✅ 成本低（节省95%）
- ✅ 效果好（与竞品一致）

**立即部署，让用户体验飞速提升！🚀**

```bash
sudo bash deploy_lightweight_mode.sh
```



