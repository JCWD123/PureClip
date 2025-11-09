"""MinIO对象存储客户端"""
from minio import Minio
from minio.error import S3Error
from backend_watermark.config.config import settings
import logging
from pathlib import Path
from datetime import timedelta

logger = logging.getLogger(__name__)


class MinioClient:
    """MinIO客户端管理类"""
    
    def __init__(self):
        self.client: Minio = None
    
    def connect(self):
        """连接到MinIO"""
        try:
            self.client = Minio(
                settings.MINIO_ENDPOINT,
                access_key=settings.MINIO_ACCESS_KEY,
                secret_key=settings.MINIO_SECRET_KEY,
                secure=settings.MINIO_SECURE
            )
            # 确保bucket存在
            if not self.client.bucket_exists(settings.MINIO_BUCKET_NAME):
                self.client.make_bucket(settings.MINIO_BUCKET_NAME)
            logger.info("MinIO连接成功")
        except Exception as e:
            logger.error(f"MinIO连接失败: {e}")
            raise
    
    def upload_file(self, file_path: str, object_name: str) -> str:
        """
        上传文件到MinIO
        
        Args:
            file_path: 本地文件路径
            object_name: MinIO中的对象名称
            
        Returns:
            文件访问URL
        """
        if self.client is None:
            self.connect()
        
        try:
            self.client.fput_object(
                settings.MINIO_BUCKET_NAME,
                object_name,
                file_path
            )
            
            # 生成访问URL（7天有效期）
            url = self.client.presigned_get_object(
                settings.MINIO_BUCKET_NAME,
                object_name,
                expires=timedelta(days=7)
            )
            
            # 如果配置了公开URL，替换endpoint
            if settings.MINIO_PUBLIC_URL:
                url = self._replace_with_public_url(url, object_name)
            
            logger.info(f"文件上传成功: {object_name}")
            logger.info(f"访问URL: {url}")
            return url
        except S3Error as e:
            logger.error(f"文件上传失败: {e}")
            raise
    
    def _replace_with_public_url(self, presigned_url: str, object_name: str) -> str:
        """
        将MinIO生成的URL替换为公开访问URL
        
        Args:
            presigned_url: MinIO生成的预签名URL
            object_name: 对象名称
            
        Returns:
            公开访问URL
        """
        # 从presigned_url中提取查询参数
        from urllib.parse import urlparse, parse_qs, urlencode
        
        parsed = urlparse(presigned_url)
        query_params = parse_qs(parsed.query)
        
        # 构建新的URL
        public_url = f"{settings.MINIO_PUBLIC_URL}/{settings.MINIO_BUCKET_NAME}/{object_name}"
        
        # 添加查询参数
        if query_params:
            query_string = urlencode({k: v[0] for k, v in query_params.items()})
            public_url = f"{public_url}?{query_string}"
        
        return public_url
    
    def download_file(self, object_name: str, file_path: str):
        """
        从MinIO下载文件
        
        Args:
            object_name: MinIO中的对象名称
            file_path: 本地保存路径
        """
        if self.client is None:
            self.connect()
        
        try:
            self.client.fget_object(
                settings.MINIO_BUCKET_NAME,
                object_name,
                file_path
            )
            logger.info(f"文件下载成功: {object_name}")
        except S3Error as e:
            logger.error(f"文件下载失败: {e}")
            raise
    
    def delete_file(self, object_name: str):
        """
        删除MinIO中的文件
        
        Args:
            object_name: MinIO中的对象名称
        """
        if self.client is None:
            self.connect()
        
        try:
            self.client.remove_object(
                settings.MINIO_BUCKET_NAME,
                object_name
            )
            logger.info(f"文件删除成功: {object_name}")
        except S3Error as e:
            logger.error(f"文件删除失败: {e}")
            raise
    
    def get_presigned_url(self, object_name: str, expires: int = 3600) -> str:
        """
        获取预签名URL
        
        Args:
            object_name: MinIO中的对象名称
            expires: 过期时间（秒）
            
        Returns:
            预签名URL
        """
        if self.client is None:
            self.connect()
        
        try:
            url = self.client.presigned_get_object(
                settings.MINIO_BUCKET_NAME,
                object_name,
                expires=timedelta(seconds=expires)
            )
            return url
        except S3Error as e:
            logger.error(f"获取预签名URL失败: {e}")
            raise


# 全局MinIO实例
minio_client = MinioClient()


def get_minio() -> MinioClient:
    """获取MinIO实例"""
    if minio_client.client is None:
        minio_client.connect()
    return minio_client


