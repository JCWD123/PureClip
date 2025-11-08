"""文件下载服务"""
import requests
import os
import uuid
from pathlib import Path
from backend_watermark.config.config import settings
from backend_watermark.models.task import MediaType
import logging

logger = logging.getLogger(__name__)


class Downloader:
    """文件下载器"""
    
    def __init__(self):
        self.temp_dir = Path(settings.VIDEO_TEMP_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def download(self, url: str, media_type: str) -> str:
        """
        下载文件
        
        Args:
            url: 文件URL
            media_type: 媒体类型
            
        Returns:
            本地文件路径
        """
        logger.info(f"开始下载文件: {url}")
        
        try:
            # 发送请求
            response = requests.get(
                url,
                stream=True,
                timeout=settings.TIMEOUT_DOWNLOAD
            )
            response.raise_for_status()
            
            # 获取文件扩展名
            content_type = response.headers.get('content-type', '')
            ext = self._get_file_extension(content_type, media_type)
            
            # 生成本地文件路径
            filename = f"{uuid.uuid4()}{ext}"
            local_path = self.temp_dir / filename
            
            # 保存文件
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"文件下载成功: {local_path}")
            return str(local_path)
            
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            raise Exception(f"下载失败: {str(e)}")
    
    def _get_file_extension(self, content_type: str, media_type: str) -> str:
        """
        获取文件扩展名
        
        Args:
            content_type: MIME类型
            media_type: 媒体类型
            
        Returns:
            文件扩展名
        """
        if media_type == MediaType.VIDEO.value:
            if 'mp4' in content_type:
                return '.mp4'
            elif 'avi' in content_type:
                return '.avi'
            elif 'mov' in content_type:
                return '.mov'
            else:
                return '.mp4'  # 默认
        else:  # IMAGE
            if 'jpeg' in content_type or 'jpg' in content_type:
                return '.jpg'
            elif 'png' in content_type:
                return '.png'
            elif 'webp' in content_type:
                return '.webp'
            else:
                return '.jpg'  # 默认


