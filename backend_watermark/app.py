"""PureClip去水印服务主应用"""
import sys
from pathlib import Path
import logging
from contextlib import asynccontextmanager

# 添加项目根目录到系统路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend_watermark.config.config import settings
from backend_watermark.core.mongodb import get_mongodb
from backend_watermark.core.redis_client import get_redis
from backend_watermark.core.minio_client import get_minio

# 导入路由
from backend_watermark.api import task_router, history_router
from backend_watermark.api.proxy import router as proxy_router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动事件
    logger.info("PureClip去水印服务启动中...")
    
    # 连接MongoDB
    try:
        db = get_mongodb()
        logger.info("MongoDB连接成功")
    except Exception as e:
        logger.error(f"MongoDB连接失败: {e}")
    
    # 连接Redis
    try:
        redis = get_redis()
        logger.info("Redis连接成功")
    except Exception as e:
        logger.error(f"Redis连接失败: {e}")
    
    # 连接MinIO
    try:
        minio = get_minio()
        logger.info("MinIO连接成功")
    except Exception as e:
        logger.error(f"MinIO连接失败: {e}")
    
    yield
    
    # 关闭事件
    logger.info("PureClip去水印服务关闭中...")
    
    # 关闭MongoDB连接
    try:
        db = get_mongodb()
        db.close()
        logger.info("MongoDB连接已关闭")
    except Exception as e:
        logger.error(f"关闭MongoDB连接失败: {e}")
    
    # 关闭Redis连接
    try:
        redis = get_redis()
        redis.close()
        logger.info("Redis连接已关闭")
    except Exception as e:
        logger.error(f"关闭Redis连接失败: {e}")


# 创建FastAPI应用
app = FastAPI(
    title="PureClip去水印服务API",
    description="视频和图片去水印处理系统",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 注册路由
app.include_router(task_router, prefix="/api", tags=["任务管理"])
app.include_router(history_router, prefix="/api", tags=["历史记录"])
app.include_router(proxy_router, prefix="/api", tags=["代理下载"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用PureClip去水印服务API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "pureclip-watermark-remover"
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"启动服务器: host={settings.HOST}, port={settings.PORT}")
    
    uvicorn.run(
        "app:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )


