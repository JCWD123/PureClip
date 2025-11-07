"""健康档案助手主应用"""
import sys
from pathlib import Path
import logging
from contextlib import asynccontextmanager

# 添加项目根目录到系统路径
ROOT_DIR = Path(__file__).parent.parent.absolute()
sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.config import settings
from backend.core.mongodb import get_mongodb
from backend.scheduler.tasks import health_scheduler

# 导入路由
from backend.api import health_profile, persona, push

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
    logger.info("健康档案助手应用启动中...")
    
    # 连接MongoDB
    try:
        db = get_mongodb()
        logger.info("MongoDB连接成功")
    except Exception as e:
        logger.error(f"MongoDB连接失败: {e}")
    
    # 启动定时任务调度器
    try:
        health_scheduler.start()
        logger.info("定时任务调度器启动成功")
    except Exception as e:
        logger.error(f"定时任务调度器启动失败: {e}")
    
    yield
    
    # 关闭事件
    logger.info("健康档案助手应用关闭中...")
    
    # 关闭MongoDB连接
    try:
        db = get_mongodb()
        db.close()
        logger.info("MongoDB连接已关闭")
    except Exception as e:
        logger.error(f"关闭MongoDB连接失败: {e}")
    
    # 关闭定时任务调度器
    try:
        health_scheduler.shutdown()
        logger.info("定时任务调度器已关闭")
    except Exception as e:
        logger.error(f"关闭定时任务调度器失败: {e}")


# 创建FastAPI应用
app = FastAPI(
    title="健康档案助手API",
    description="个性化健康资讯推送系统",
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
app.include_router(health_profile.router, prefix="/api", tags=["健康档案"])
app.include_router(persona.router, prefix="/api", tags=["人物风格"])
app.include_router(push.router, prefix="/api", tags=["健康推送"])


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "欢迎使用健康档案助手API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "ok",
        "message": "服务运行正常"
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





