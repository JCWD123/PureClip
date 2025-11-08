"""文件下载服务"""
import requests
import os
import uuid
from pathlib import Path
from backend_watermark.config.config import settings
from backend_watermark.models.task import MediaType
import logging

logger = logging.getLogger(__name__)

# 延迟导入避免循环依赖
def get_video_parser():
    """延迟导入VideoParser"""
    from backend_watermark.services.video_parser import get_video_parser as _get_parser
    return _get_parser()


class Downloader:
    """文件下载器"""
    
    def __init__(self):
        self.temp_dir = Path(settings.VIDEO_TEMP_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        # 创建Session以支持Cookie和连接复用
        self.session = requests.Session()
    
    def _get_browser_headers(self, url: str) -> dict:
        """
        生成浏览器请求头，伪装成真实浏览器
        
        Args:
            url: 目标URL
            
        Returns:
            请求头字典
        """
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }
        
        # 根据不同平台添加特定的Referer
        if 'douyin.com' in url:
            headers['Referer'] = 'https://www.douyin.com/'
        elif 'baidu.com' in url:
            headers['Referer'] = 'https://www.baidu.com/'
        elif 'xhslink.com' in url or 'xiaohongshu.com' in url:
            headers['Referer'] = 'https://www.xiaohongshu.com/'
        elif 'kuaishou.com' in url:
            headers['Referer'] = 'https://www.kuaishou.com/'
        elif 'bilibili.com' in url or 'b23.tv' in url:
            headers['Referer'] = 'https://www.bilibili.com/'
        
        return headers
    
    def download(self, url: str, media_type: str) -> str:
        """
        下载文件（支持URL解析、浏览器伪装和自动跟随重定向）
        
        Args:
            url: 文件URL或短链
            media_type: 媒体类型
            
        Returns:
            本地文件路径
        """
        logger.info(f"开始下载文件: {url}")
        
        try:
            # 步骤1: 尝试解析URL（针对短链和平台链接）
            parsed_url = self._parse_video_url(url, media_type)
            if parsed_url and parsed_url != url:
                logger.info(f"URL解析成功，使用解析后的地址: {parsed_url}")
                url = parsed_url
            
            # 步骤2: 获取浏览器请求头
            headers = self._get_browser_headers(url)
            
            # 发送请求（自动跟随重定向）
            response = self.session.get(
                url,
                headers=headers,
                stream=True,
                timeout=settings.TIMEOUT_DOWNLOAD,
                allow_redirects=True,  # 显式允许重定向
                verify=True  # 验证SSL证书
            )
            response.raise_for_status()
            
            # 检查最终URL（可能经过多次重定向）
            final_url = response.url
            if final_url != url:
                logger.info(f"URL重定向: {url} -> {final_url}")
            
            # 获取文件扩展名
            content_type = response.headers.get('content-type', '')
            logger.info(f"Content-Type: {content_type}")
            
            # 验证是否为有效的媒体文件
            if not self._is_valid_media_content(content_type, media_type):
                logger.warning(f"可能不是有效的媒体文件，Content-Type: {content_type}")
                # 记录响应内容的前200字节用于调试
                response_preview = response.content[:200] if len(response.content) > 0 else b""
                logger.warning(f"响应预览: {response_preview}")
                
                # 检测是否为验证码页面
                if self._is_captcha_page(final_url, response.content):
                    error_msg = self._get_captcha_error_message(final_url)
                    logger.error(error_msg)
                    raise Exception(error_msg)
            
            ext = self._get_file_extension(content_type, media_type)
            
            # 生成本地文件路径
            filename = f"{uuid.uuid4()}{ext}"
            local_path = self.temp_dir / filename
            
            # 保存文件
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            # 检查文件大小
            file_size = os.path.getsize(local_path)
            logger.info(f"文件下载成功: {local_path} (大小: {file_size} bytes)")
            
            # 如果文件太小，可能是错误页面
            if file_size < 1024:  # 小于1KB
                logger.warning(f"下载的文件过小({file_size} bytes)，可能不是有效的媒体文件")
            
            return str(local_path)
            
        except Exception as e:
            logger.error(f"文件下载失败: {e}")
            raise Exception(f"下载失败: {str(e)}")
    
    def _parse_video_url(self, url: str, media_type: str) -> str:
        """
        解析视频URL（针对短链和平台链接）
        
        Args:
            url: 原始URL
            media_type: 媒体类型
            
        Returns:
            解析后的真实URL
        """
        # 只对视频类型尝试解析
        if media_type != MediaType.VIDEO.value:
            return url
        
        try:
            # 检测是否需要解析
            needs_parse = any([
                'mr.baidu.com' in url,
                'v.douyin.com' in url,
                'xhslink.com' in url,
                'b23.tv' in url,
                '/share' in url.lower(),
                '/r/' in url
            ])
            
            if not needs_parse:
                logger.info("URL无需解析，直接下载")
                return url
            
            # 使用视频解析器
            logger.info("检测到短链或平台链接，尝试解析...")
            parser = get_video_parser()
            result = parser.parse(url)
            
            if result['success'] and result['video_url']:
                logger.info(f"视频解析成功: {result.get('title', 'Unknown')}")
                logger.info(f"作者: {result.get('author', 'Unknown')}")
                logger.info(f"平台: {result.get('platform', 'Unknown')}")
                return result['video_url']
            else:
                logger.warning(f"视频解析失败: {result.get('error', 'Unknown')}")
                return url
                
        except Exception as e:
            logger.warning(f"URL解析异常: {e}，将使用原始URL")
            return url
    
    def _is_captcha_page(self, url: str, content: bytes) -> bool:
        """
        检测是否为验证码页面
        
        Args:
            url: 最终URL
            content: 响应内容
            
        Returns:
            是否为验证码页面
        """
        # 检查URL中的验证码关键词
        captcha_url_patterns = [
            'captcha', 'verify', 'tuxing', 'slider', 
            'wappass.baidu.com', 'verify.snssdk.com'
        ]
        
        url_lower = url.lower()
        if any(pattern in url_lower for pattern in captcha_url_patterns):
            return True
        
        # 检查响应内容中的验证码关键词
        try:
            content_str = content[:1000].decode('utf-8', errors='ignore').lower()
            captcha_content_patterns = [
                '安全验证', '验证码', 'captcha', '人机验证',
                'security verification', '滑动验证'
            ]
            if any(pattern in content_str for pattern in captcha_content_patterns):
                return True
        except:
            pass
        
        return False
    
    def _get_captcha_error_message(self, url: str) -> str:
        """
        生成验证码错误消息
        
        Args:
            url: 验证码页面URL
            
        Returns:
            错误消息
        """
        platform = ""
        if 'baidu.com' in url:
            platform = "百度"
        elif 'douyin.com' in url or 'snssdk.com' in url:
            platform = "抖音"
        elif 'xiaohongshu.com' in url or 'xhslink.com' in url:
            platform = "小红书"
        else:
            platform = "该平台"
        
        return (
            f"❌ {platform}链接需要人机验证，无法直接下载。\n"
            f"建议：\n"
            f"1. 在浏览器中打开该链接，完成验证后获取真实的视频URL\n"
            f"2. 使用其他平台的公开视频链接\n"
            f"3. 如果是{platform}APP分享的链接，请尝试获取原始视频地址\n"
            f"验证码页面: {url[:100]}..."
        )
    
    def _is_valid_media_content(self, content_type: str, media_type: str) -> bool:
        """
        验证Content-Type是否为有效的媒体文件
        
        Args:
            content_type: MIME类型
            media_type: 媒体类型
            
        Returns:
            是否为有效的媒体文件
        """
        content_type_lower = content_type.lower()
        
        # 排除HTML和文本类型
        invalid_types = ['text/html', 'text/plain', 'application/json', 'application/xml']
        for invalid_type in invalid_types:
            if invalid_type in content_type_lower:
                return False
        
        # 检查是否为媒体类型
        if media_type == MediaType.VIDEO.value:
            valid_patterns = ['video/', 'application/octet-stream', 'binary/octet-stream']
            return any(pattern in content_type_lower for pattern in valid_patterns)
        else:  # IMAGE
            valid_patterns = ['image/', 'application/octet-stream', 'binary/octet-stream']
            return any(pattern in content_type_lower for pattern in valid_patterns)
    
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
            elif 'quicktime' in content_type:
                return '.mov'
            elif 'x-msvideo' in content_type:
                return '.avi'
            elif 'octet-stream' in content_type:
                return '.mp4'  # 二进制流默认为mp4
            else:
                return '.mp4'  # 默认
        else:  # IMAGE
            if 'jpeg' in content_type or 'jpg' in content_type:
                return '.jpg'
            elif 'png' in content_type:
                return '.png'
            elif 'webp' in content_type:
                return '.webp'
            elif 'gif' in content_type:
                return '.gif'
            elif 'octet-stream' in content_type:
                return '.jpg'  # 二进制流默认为jpg
            else:
                return '.jpg'  # 默认


