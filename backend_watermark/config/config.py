"""配置管理"""
import os
import yaml
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any

# 获取项目根目录
ROOT_DIR = Path(__file__).parent.parent.parent.absolute()
CONFIG_FILE = os.path.join(Path(__file__).parent, "config.yaml")

# 加载YAML配置
with open(CONFIG_FILE, "r", encoding="utf-8") as file:
    yaml_config = yaml.safe_load(file)


class Settings(BaseSettings):
    """应用配置类"""
    
    # 项目根目录
    ROOT_DIR: Path = ROOT_DIR
    
    # 服务器设置
    HOST: str = yaml_config["server"]["host"]
    PORT: int = yaml_config["server"]["port"]
    DEBUG: bool = yaml_config["server"]["debug"]
    
    # MongoDB配置
    MONGODB_URI: str = yaml_config["mongodb"]["uri"]
    MONGODB_DATABASE: str = yaml_config["mongodb"]["database"]
    COLLECTION_TASKS: str = yaml_config["mongodb"]["collection_tasks"]
    COLLECTION_HISTORY: str = yaml_config["mongodb"]["collection_history"]
    
    # Redis配置
    REDIS_HOST: str = yaml_config["redis"]["host"]
    REDIS_PORT: int = yaml_config["redis"]["port"]
    REDIS_DB: int = yaml_config["redis"]["db"]
    REDIS_PASSWORD: Optional[str] = yaml_config["redis"]["password"]
    
    # MinIO配置
    MINIO_ENDPOINT: str = yaml_config["minio"]["endpoint"]
    MINIO_ACCESS_KEY: str = yaml_config["minio"]["access_key"]
    MINIO_SECRET_KEY: str = yaml_config["minio"]["secret_key"]
    MINIO_BUCKET_NAME: str = yaml_config["minio"]["bucket_name"]
    MINIO_SECURE: bool = yaml_config["minio"]["secure"]
    
    # Celery配置
    CELERY_BROKER_URL: str = yaml_config["celery"]["broker_url"]
    CELERY_RESULT_BACKEND: str = yaml_config["celery"]["result_backend"]
    CELERY_TASK_SERIALIZER: str = yaml_config["celery"]["task_serializer"]
    CELERY_RESULT_SERIALIZER: str = yaml_config["celery"]["result_serializer"]
    CELERY_ACCEPT_CONTENT: list = yaml_config["celery"]["accept_content"]
    CELERY_TIMEZONE: str = yaml_config["celery"]["timezone"]
    CELERY_ENABLE_UTC: bool = yaml_config["celery"]["enable_utc"]
    
    # 视频处理配置
    VIDEO_MAX_SIZE_MB: int = yaml_config["video"]["max_size_mb"]
    VIDEO_MAX_DURATION_SECONDS: int = yaml_config["video"]["max_duration_seconds"]
    VIDEO_OUTPUT_FORMAT: str = yaml_config["video"]["output_format"]
    VIDEO_TEMP_DIR: str = yaml_config["video"]["temp_dir"]
    
    # 图片处理配置
    IMAGE_MAX_SIZE_MB: int = yaml_config["image"]["max_size_mb"]
    IMAGE_OUTPUT_FORMAT: str = yaml_config["image"]["output_format"]
    IMAGE_QUALITY: int = yaml_config["image"]["quality"]
    
    # 去水印方法配置
    WATERMARK_METHODS: Dict[str, Any] = yaml_config["watermark"]["methods"]
    
    # 超时配置
    TIMEOUT_DOWNLOAD: int = yaml_config["timeout"]["download"]
    TIMEOUT_PROCESS: int = yaml_config["timeout"]["process"]
    TIMEOUT_UPLOAD: int = yaml_config["timeout"]["upload"]
    
    # 视频解析API配置
    IIILAB_CLIENT_ID: str = yaml_config["video_parser"]["iiilab"]["client_id"]
    IIILAB_CLIENT_SECRET: str = yaml_config["video_parser"]["iiilab"]["client_secret"]
    IIILAB_API_URL: str = yaml_config["video_parser"]["iiilab"]["api_url"]
    IIILAB_TIMEOUT: int = yaml_config["video_parser"]["iiilab"]["timeout"]
    
    # JWT配置（用于用户认证）
    SECRET_KEY: str = "pureclip-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30天
    
    @property
    def redis_url(self) -> str:
        """获取Redis连接URL"""
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    class Config:
        env_file = os.path.join(ROOT_DIR, ".env")
        env_file_encoding = "utf-8"


# 实例化设置
settings = Settings()


