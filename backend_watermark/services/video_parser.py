"""视频URL解析服务 - 支持多平台短链解析"""
import requests
import logging
import re
from typing import Optional, Dict, Any
from backend_watermark.utils.url_extractor import detect_platform
from backend_watermark.config.config import settings

logger = logging.getLogger(__name__)


class VideoParser:
    """视频URL解析器 - 解析各平台短链获取真实视频地址"""
    
    def __init__(self):
        self.timeout = settings.IIILAB_TIMEOUT
        # 多个解析API作为备份
        self.apis = [
            {
                'name': 'iiilab',
                'url': settings.IIILAB_API_URL,
                'method': 'POST',
                'params_key': 'url'
            },
            # 可以添加更多备用API
        ]
    
    def parse(self, url: str) -> Dict[str, Any]:
        """
        解析视频链接，获取真实下载地址
        
        Args:
            url: 短链或视频链接
            
        Returns:
            解析结果字典:
            {
                'success': True/False,
                'video_url': '真实视频URL',
                'title': '视频标题',
                'cover': '封面图URL',
                'author': '作者',
                'platform': '平台名称',
                'error': '错误信息'
            }
        """
        logger.info(f"开始解析视频链接: {url}")
        
        # 检测平台
        platform = detect_platform(url)
        logger.info(f"检测到平台: {platform}")
        
        # 如果是直接的视频URL，不需要解析
        if self._is_direct_video_url(url):
            logger.info("检测到直接视频链接，无需解析")
            return {
                'success': True,
                'video_url': url,
                'title': None,
                'cover': None,
                'author': None,
                'platform': 'direct',
                'error': None
            }
        
        # 尝试使用各个API解析
        for api in self.apis:
            try:
                result = self._parse_with_api(url, api, platform)
                if result['success']:
                    logger.info(f"解析成功，使用API: {api['name']}")
                    return result
            except Exception as e:
                logger.warning(f"API {api['name']} 解析失败: {e}")
                continue
        
        # 所有API都失败，尝试直接下载（可能是公开链接）
        logger.warning("所有解析API失败，尝试直接使用原始URL")
        return {
            'success': False,
            'video_url': url,  # 返回原始URL，让下载器尝试
            'title': None,
            'cover': None,
            'author': None,
            'platform': platform,
            'error': '无法解析该链接，将尝试直接下载'
        }
    
    def _is_direct_video_url(self, url: str) -> bool:
        """
        判断是否为直接的视频URL
        
        Args:
            url: URL地址
            
        Returns:
            是否为直接视频URL
        """
        video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.flv', '.webm', '.m3u8']
        url_lower = url.lower()
        
        # 检查URL是否包含视频扩展名
        if any(ext in url_lower for ext in video_extensions):
            return True
        
        # 检查是否为CDN或云存储链接
        cdn_patterns = [
            'vd3.bdstatic.com',  # 百度CDN
            'aweme.snssdk.com',  # 抖音CDN
            'v.cdn.',
            'video.',
            'cdn.',
            'oss-',
            'cos.',
            's3.',
            'cloudfront.net',
        ]
        
        if any(pattern in url_lower for pattern in cdn_patterns):
            return True
        
        return False
    
    def _parse_with_api(
        self, 
        url: str, 
        api: Dict[str, str],
        platform: str
    ) -> Dict[str, Any]:
        """
        使用指定API解析视频链接
        
        Args:
            url: 视频链接
            api: API配置
            platform: 平台名称
            
        Returns:
            解析结果
        """
        try:
            # 构建请求
            if api['method'] == 'GET':
                response = requests.get(
                    api['url'],
                    params={api['params_key']: url},
                    timeout=self.timeout,
                    headers=self._get_headers()
                )
            else:  # POST
                response = requests.post(
                    api['url'],
                    json={api['params_key']: url},
                    timeout=self.timeout,
                    headers=self._get_headers()
                )
            
            response.raise_for_status()
            data = response.json()
            
            # 解析响应（根据不同API调整）
            return self._parse_api_response(data, platform)
            
        except Exception as e:
            logger.error(f"API请求失败: {e}")
            raise
    
    def _parse_api_response(self, data: Dict, platform: str) -> Dict[str, Any]:
        """
        解析API响应数据
        
        Args:
            data: API返回的JSON数据
            platform: 平台名称
            
        Returns:
            标准化的解析结果
        """
        # iiilab API 实际响应格式（根据真实日志）
        # 成功: {"text": "标题", "medias": [{"media_type": "video", "resource_url": "...", "preview_url": "..."}], "overseas": 0}
        # 或旧格式: {"code": 200, "message": "success", "data": {...}}
        
        logger.info(f"API响应数据: {data}")
        
        # 格式1: iiilab 新格式（实际使用的格式）
        if 'medias' in data and isinstance(data['medias'], list) and len(data['medias']) > 0:
            medias = data['medias']
            video_media = None
            
            # 查找视频类型的media
            for media in medias:
                if media.get('media_type') == 'video':
                    video_media = media
                    break
            
            # 如果没找到视频，取第一个
            if not video_media and len(medias) > 0:
                video_media = medias[0]
            
            if video_media and video_media.get('resource_url'):
                video_url = video_media['resource_url']
                logger.info(f"✅ 从medias中提取到视频URL: {video_url[:100]}...")
                
                return {
                    'success': True,
                    'video_url': video_url,
                    'title': data.get('text') or data.get('title'),
                    'cover': video_media.get('preview_url') or video_media.get('cover'),
                    'author': data.get('author') or data.get('nickname'),
                    'platform': platform,
                    'error': None
                }
            else:
                logger.warning(f"medias中未找到有效的视频URL，响应数据: {video_media}")
                return {
                    'success': False,
                    'video_url': None,
                    'title': None,
                    'cover': None,
                    'author': None,
                    'platform': platform,
                    'error': 'medias中未找到视频URL'
                }
        
        # 格式2: 标准格式（code=200）
        elif data.get('code') == 200:
            video_data = data.get('data', {})
            
            # iiilab 可能返回多个视频，取第一个
            if isinstance(video_data, list) and len(video_data) > 0:
                video_data = video_data[0]
            
            # 提取视频URL（可能在不同字段）
            video_url = (
                video_data.get('url') or 
                video_data.get('video_url') or 
                video_data.get('play') or 
                video_data.get('videoUrl') or
                video_data.get('playUrl') or
                video_data.get('resource_url')
            )
            
            if not video_url:
                logger.warning(f"未找到视频URL，响应数据: {video_data}")
                return {
                    'success': False,
                    'video_url': None,
                    'title': None,
                    'cover': None,
                    'author': None,
                    'platform': platform,
                    'error': '响应中未找到视频URL'
                }
            
            return {
                'success': True,
                'video_url': video_url,
                'title': video_data.get('title') or video_data.get('desc') or video_data.get('text'),
                'cover': video_data.get('cover') or video_data.get('thumbnail') or video_data.get('coverUrl'),
                'author': video_data.get('author') or video_data.get('nickname') or video_data.get('authorName'),
                'platform': platform,
                'error': None
            }
        
        # 格式3: 错误响应
        else:
            error_msg = data.get('message') or data.get('msg') or data.get('error') or '解析失败'
            logger.error(f"API解析失败: {error_msg}，响应数据: {data}")
            return {
                'success': False,
                'video_url': None,
                'title': None,
                'cover': None,
                'author': None,
                'platform': platform,
                'error': error_msg
            }
    
    def _get_headers(self) -> Dict[str, str]:
        """
        获取请求头（iiilab格式）
        
        Returns:
            请求头字典
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'x-client-id': settings.IIILAB_CLIENT_ID,
            'x-client-secret': settings.IIILAB_CLIENT_SECRET
        }
    
    def parse_baidu_url(self, url: str) -> Optional[str]:
        """
        专门处理百度链接的解析
        
        Args:
            url: 百度短链
            
        Returns:
            真实视频URL或None
        """
        logger.info("使用百度专用解析器")
        
        try:
            # 方法1: 尝试提取nid参数，构造API地址
            nid_match = re.search(r'nid=([^&]+)', url)
            if nid_match:
                nid = nid_match.group(1)
                # 百度视频API（可能需要调整）
                api_url = f"https://mbd.baidu.com/ma/s/api/video?nid={nid}"
                
                response = requests.get(
                    api_url,
                    headers=self._get_baidu_headers(),
                    timeout=self.timeout
                )
                
                data = response.json()
                video_url = data.get('data', {}).get('video', {}).get('url')
                
                if video_url:
                    logger.info(f"百度解析成功: {video_url}")
                    return video_url
            
            # 方法2: 使用第三方解析服务
            # （这里可以集成具体的解析服务）
            
        except Exception as e:
            logger.error(f"百度链接解析失败: {e}")
        
        return None
    
    def _get_baidu_headers(self) -> Dict[str, str]:
        """
        获取百度专用请求头
        
        Returns:
            请求头字典
        """
        return {
            'User-Agent': 'Mozilla/5.0 (Linux; Android 12; M2102J2SC) AppleWebKit/537.36',
            'Referer': 'https://www.baidu.com/',
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        }


# 单例模式
_parser_instance = None

def get_video_parser() -> VideoParser:
    """获取视频解析器单例"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = VideoParser()
    return _parser_instance

