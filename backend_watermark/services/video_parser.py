"""视频URL解析服务 - 支持多平台短链解析"""
import requests
import logging
import re
from typing import Optional, Dict, Any
from lxml import etree
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
        
        # ✅ 特殊平台专门处理（iiilab不支持）
        if platform == 'jimeng':
            logger.info("检测到即梦AI平台，使用专门解析器")
            return self.parse_jimeng_url(url)
        
        if platform == 'qq':
            logger.info("检测到QQ浏览器平台，使用专门解析器")
            return self.parse_qq_url(url)
        
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
    
    def parse_jimeng_url(self, url: str) -> Dict[str, Any]:
        """
        专门处理即梦AI链接的解析
        即梦是剪映旗下的AI生成内容平台
        
        解析策略：
        1. 访问即梦分享页面
        2. 使用xpath定位<video>标签
        3. 提取video标签的src属性作为真实视频URL
        4. 返回标准化的iiilab格式数据
        
        Args:
            url: 即梦分享链接 (例如: https://jimeng.jianying.com/s/bYeEyb6ThwU/?t=210)
            
        Returns:
            解析结果 (与iiilab接口格式一致):
            {
                'success': True/False,
                'video_url': '真实视频URL',
                'title': '视频标题',
                'cover': '封面图URL',
                'author': '作者',
                'platform': 'jimeng',
                'error': None
            }
        """
        logger.info(f"🎬 使用即梦AI专用解析器")
        logger.info(f"📎 分享链接: {url}")
        
        try:
            # 1️⃣ 请求即梦分享页面
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.38',
                'Referer': 'https://jimeng.jianying.com/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            
            logger.info(f"📡 正在请求即梦页面...")
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            html_content = response.text
            logger.info(f"✅ 页面获取成功，大小: {len(html_content)} bytes")
            
            # 2️⃣ 使用lxml解析HTML
            try:
                # 使用HTMLParser解析HTML（容错能力强）
                parser = etree.HTMLParser(encoding='utf-8')
                tree = etree.fromstring(html_content, parser)
                
                logger.info(f"✅ HTML解析成功")
                
                # 3️⃣ 使用xpath定位<video>标签的src属性
                # xpath语法：//video/@src 表示获取所有video标签的src属性
                video_srcs = tree.xpath('//video/@src')
                
                if video_srcs and len(video_srcs) > 0:
                    # 获取第一个video标签的src
                    video_url = video_srcs[0]
                    
                    # URL可能被HTML转义，需要反转义
                    # 例如: &amp; -> &
                    import html
                    video_url = html.unescape(video_url)
                    
                    logger.info(f"✅ 成功定位到<video>标签")
                    logger.info(f"🎥 视频URL: {video_url[:100]}...")
                    
                    # 4️⃣ 提取标题（尝试多个可能的位置）
                    title = None
                    
                    # 尝试从<title>标签提取
                    title_elements = tree.xpath('//title/text()')
                    if title_elements:
                        title = title_elements[0].strip()
                    
                    # 尝试从meta标签提取
                    if not title:
                        meta_titles = tree.xpath('//meta[@property="og:title"]/@content')
                        if meta_titles:
                            title = meta_titles[0].strip()
                    
                    # 尝试从h1标签提取
                    if not title:
                        h1_elements = tree.xpath('//h1/text()')
                        if h1_elements:
                            title = h1_elements[0].strip()
                    
                    # 默认标题
                    if not title:
                        title = '即梦AI作品'
                    
                    logger.info(f"📝 标题: {title}")
                    
                    # 5️⃣ 提取封面图（可选）
                    cover = None
                    
                    # 尝试从video标签的poster属性提取
                    poster_urls = tree.xpath('//video/@poster')
                    if poster_urls:
                        cover = html.unescape(poster_urls[0])
                    
                    # 尝试从meta标签提取
                    if not cover:
                        meta_images = tree.xpath('//meta[@property="og:image"]/@content')
                        if meta_images:
                            cover = meta_images[0]
                    
                    if cover:
                        logger.info(f"🖼️ 封面: {cover[:100]}...")
                    
                    # 6️⃣ 返回标准化格式（与iiilab接口一致）
                    return {
                        'success': True,
                        'video_url': video_url,
                        'title': title,
                        'cover': cover,
                        'author': None,  # 即梦页面暂不提供作者信息
                        'platform': 'jimeng',
                        'error': None
                    }
                
                else:
                    # 没有找到video标签
                    logger.warning("⚠️ 页面中未找到<video>标签")
                    logger.info(f"📄 页面预览: {html_content[:500]}...")
                    
                    return {
                        'success': False,
                        'video_url': None,
                        'title': None,
                        'cover': None,
                        'author': None,
                        'platform': 'jimeng',
                        'error': '即梦页面中未找到视频标签，可能需要登录或该链接已失效'
                    }
            
            except etree.ParseError as e:
                logger.error(f"❌ HTML解析失败: {e}")
                logger.info(f"📄 HTML内容预览: {html_content[:500]}...")
                
                return {
                    'success': False,
                    'video_url': None,
                    'title': None,
                    'cover': None,
                    'author': None,
                    'platform': 'jimeng',
                    'error': f'即梦页面HTML解析失败: {str(e)}'
                }
            
        except requests.RequestException as e:
            logger.error(f"❌ 即梦页面请求失败: {e}")
            return {
                'success': False,
                'video_url': None,
                'title': None,
                'cover': None,
                'author': None,
                'platform': 'jimeng',
                'error': f'即梦页面请求失败: {str(e)}'
            }
        
        except Exception as e:
            logger.error(f"❌ 即梦链接解析失败: {e}")
            return {
                'success': False,
                'video_url': None,
                'title': None,
                'cover': None,
                'author': None,
                'platform': 'jimeng',
                'error': f'即梦链接解析失败: {str(e)}'
            }
    
    def parse_qq_url(self, url: str) -> Dict[str, Any]:
        """
        专门处理QQ浏览器视频链接的解析
        
        Args:
            url: QQ浏览器分享链接 (例如: https://newsa.html5.qq.com/v1/share-video?vid=...)
            
        Returns:
            解析结果
        """
        logger.info(f"使用QQ浏览器专用解析器: {url}")
        
        try:
            # 提取vid参数
            vid_match = re.search(r'vid=([^&]+)', url)
            if not vid_match:
                logger.warning("QQ链接中未找到vid参数")
                return {
                    'success': False,
                    'video_url': None,
                    'title': None,
                    'cover': None,
                    'author': None,
                    'platform': 'qq',
                    'error': 'QQ链接格式错误：未找到vid参数'
                }
            
            vid = vid_match.group(1)
            logger.info(f"提取到视频ID: {vid}")
            
            # 方法1: 直接访问页面，尝试提取视频URL
            headers = {
                'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 QQ/8.9.0',
                'Referer': 'https://newsa.html5.qq.com/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
            }
            
            response = requests.get(url, headers=headers, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            
            html_content = response.text
            logger.info(f"QQ页面获取成功，长度: {len(html_content)}")
            
            # 尝试从HTML中提取视频URL
            video_url_patterns = [
                r'"videoUrl":\s*"([^"]+)"',
                r'"video_url":\s*"([^"]+)"',
                r'"url":\s*"(https://[^"]*\.mp4[^"]*)"',
                r'"playurl":\s*"([^"]+)"',
                r'"playUrl":\s*"([^"]+)"',
                r'<video[^>]*src="([^"]+)"',
                r'"src":\s*"(https://[^"]*\.mp4[^"]*)"',
            ]
            
            video_url = None
            for pattern in video_url_patterns:
                match = re.search(pattern, html_content)
                if match:
                    video_url = match.group(1)
                    # URL可能被转义，需要解码
                    video_url = video_url.replace('\\/', '/')
                    logger.info(f"✅ 从QQ页面提取到视频URL: {video_url[:100]}...")
                    break
            
            if video_url:
                # 提取标题
                title_match = re.search(r'"title":\s*"([^"]+)"', html_content)
                title = title_match.group(1) if title_match else None
                
                # 提取封面
                cover_match = re.search(r'"cover":\s*"([^"]+)"', html_content)
                cover = cover_match.group(1) if cover_match else None
                
                return {
                    'success': True,
                    'video_url': video_url,
                    'title': title or 'QQ浏览器视频',
                    'cover': cover,
                    'author': None,
                    'platform': 'qq',
                    'error': None
                }
            
            # 方法2: 尝试构造腾讯视频API
            # QQ浏览器的视频可能存储在腾讯视频CDN
            api_urls = [
                f"https://newsa.html5.qq.com/api/video/info?vid={vid}",
                f"https://h5vv.video.qq.com/getinfo?vid={vid}",
                f"https://vv.video.qq.com/getinfo?vids={vid}",
            ]
            
            for api_url in api_urls:
                try:
                    api_response = requests.get(api_url, headers=headers, timeout=self.timeout)
                    if api_response.status_code == 200:
                        # 尝试解析JSON
                        try:
                            api_data = api_response.json()
                            logger.info(f"QQ API响应: {api_data}")
                            
                            # 尝试从API响应中提取视频URL
                            video_data = api_data.get('data', {}) or api_data.get('vl', {})
                            if isinstance(video_data, list) and len(video_data) > 0:
                                video_data = video_data[0]
                            
                            video_url = (
                                video_data.get('url') or
                                video_data.get('fvkey') or
                                video_data.get('fn') or
                                video_data.get('ul', {}).get('ui', [{}])[0].get('url')
                            )
                            
                            if video_url:
                                return {
                                    'success': True,
                                    'video_url': video_url,
                                    'title': video_data.get('title') or video_data.get('ti') or 'QQ浏览器视频',
                                    'cover': video_data.get('cover') or video_data.get('pic'),
                                    'author': None,
                                    'platform': 'qq',
                                    'error': None
                                }
                        except:
                            # 不是JSON，继续下一个API
                            continue
                except:
                    continue
            
            # 如果都失败了
            logger.warning("QQ链接解析失败：未能提取视频URL")
            return {
                'success': False,
                'video_url': None,
                'title': None,
                'cover': None,
                'author': None,
                'platform': 'qq',
                'error': 'QQ浏览器平台暂不支持自动解析，请使用其他平台链接'
            }
            
        except Exception as e:
            logger.error(f"QQ链接解析失败: {e}")
            return {
                'success': False,
                'video_url': None,
                'title': None,
                'cover': None,
                'author': None,
                'platform': 'qq',
                'error': f'QQ链接解析失败: {str(e)}'
            }


# 单例模式
_parser_instance = None

def get_video_parser() -> VideoParser:
    """获取视频解析器单例"""
    global _parser_instance
    if _parser_instance is None:
        _parser_instance = VideoParser()
    return _parser_instance

