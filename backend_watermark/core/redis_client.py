"""Redis缓存客户端"""
import redis
from backend_watermark.config.config import settings
import logging
import json
from typing import Any, Optional
from datetime import datetime
from bson import ObjectId

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis客户端管理类"""
    
    def __init__(self):
        self.client: redis.Redis = None
    
    def connect(self):
        """连接到Redis"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                password=settings.REDIS_PASSWORD,
                decode_responses=True
            )
            # 测试连接
            self.client.ping()
            logger.info("Redis连接成功")
        except Exception as e:
            logger.error(f"Redis连接失败: {e}")
            raise
    
    def close(self):
        """关闭Redis连接"""
        if self.client is not None:
            self.client.close()
            logger.info("Redis连接已关闭")
    
    def get(self, key: str) -> Optional[Any]:
        """获取缓存"""
        if self.client is None:
            self.connect()
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis获取失败: {e}")
            return None
    
    def set(self, key: str, value: Any, expire: int = None):
        """设置缓存"""
        if self.client is None:
            self.connect()
        try:
            # 处理datetime对象
            serialized_value = json.dumps(value, default=self._json_serializer)
            self.client.set(key, serialized_value, ex=expire)
        except Exception as e:
            logger.error(f"Redis设置失败: {e}")
    
    def delete(self, key: str):
        """删除缓存"""
        if self.client is None:
            self.connect()
        try:
            self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis删除失败: {e}")
    
    def exists(self, key: str) -> bool:
        """检查键是否存在"""
        if self.client is None:
            self.connect()
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Redis检查失败: {e}")
            return False
    
    @staticmethod
    def _json_serializer(obj):
        """JSON序列化器，处理datetime和ObjectId对象"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        if isinstance(obj, ObjectId):
            return str(obj)
        raise TypeError(f"Type {type(obj)} not serializable")


# 全局Redis实例
redis_client = RedisClient()


def get_redis() -> RedisClient:
    """获取Redis实例"""
    if redis_client.client is None:
        redis_client.connect()
    return redis_client


