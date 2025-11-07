"""MongoDB数据库连接管理"""
from pymongo import MongoClient
from pymongo.database import Database
from backend.config.config import settings
import logging

logger = logging.getLogger(__name__)


class MongoDB:
    """MongoDB连接管理类"""
    
    def __init__(self):
        self.client: MongoClient = None
        self.db: Database = None
    
    def connect(self):
        """连接到MongoDB数据库"""
        try:
            self.client = MongoClient(settings.MONGODB_URI)
            self.db = self.client[settings.MONGODB_DATABASE]
            # 测试连接
            self.client.admin.command('ping')
            logger.info("MongoDB连接成功")
        except Exception as e:
            logger.error(f"MongoDB连接失败: {e}")
            raise
    
    def close(self):
        """关闭MongoDB连接"""
        if self.client is not None:
            self.client.close()
            logger.info("MongoDB连接已关闭")
    
    def get_collection(self, collection_name: str):
        """获取指定集合"""
        if self.db is None:
            self.connect()
        return self.db[collection_name]


# 全局MongoDB实例
mongodb = MongoDB()


def get_mongodb() -> MongoDB:
    """获取MongoDB实例"""
    if mongodb.client is None:
        mongodb.connect()
    return mongodb

