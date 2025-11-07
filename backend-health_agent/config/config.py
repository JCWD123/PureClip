import os
import yaml
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import List

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
    
    # 阿里云百炼配置
    DASHSCOPE_URL: str = yaml_config["dashscope"]["url"]
    DASHSCOPE_API_KEY: str = yaml_config["dashscope"]["api_key"]
    DASHSCOPE_MODEL: str = yaml_config["dashscope"]["model"]
    
    # MongoDB配置
    MONGODB_URI: str = yaml_config["mongodb"]["uri"]
    MONGODB_DATABASE: str = yaml_config["mongodb"]["database"]
    COLLECTION_HEALTH_PROFILE: str = yaml_config["mongodb"]["collection_health_profile"]
    COLLECTION_PUSH_HISTORY: str = yaml_config["mongodb"]["collection_push_history"]
    COLLECTION_PERSONA_STYLES: str = yaml_config["mongodb"]["collection_persona_styles"]
    
    # 定时任务配置
    SCHEDULER_TIMEZONE: str = yaml_config["scheduler"]["timezone"]
    REST_TIMES: List[str] = yaml_config["scheduler"]["rest_times"]
    MEAL_TIMES: List[str] = yaml_config["scheduler"]["meal_times"]
    WEATHER_TIME: str = yaml_config["scheduler"]["weather_time"]
    HEALTH_TIP_TIME: str = yaml_config["scheduler"]["health_tip_time"]
    
    # JWT配置（用于用户认证）
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天
    
    class Config:
        env_file = os.path.join(ROOT_DIR, ".env")
        env_file_encoding = "utf-8"


# 实例化设置
settings = Settings()






