"""URL提取工具"""
import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def extract_url(text: str) -> Optional[str]:
    """
    从文本中提取URL
    
    支持的场景：
    1. 纯URL: https://example.com/video.mp4
    2. 带文字的复制内容: "观看这个视频 https://example.com/video.mp4 很精彩"
    3. 多个URL: 提取第一个有效URL
    4. 微信/抖音/快手等分享链接
    
    Args:
        text: 用户输入的文本
        
    Returns:
        提取的URL，如果没有找到返回None
    """
    if not text or not isinstance(text, str):
        return None
    
    # 去除首尾空格
    text = text.strip()
    
    # 如果本身就是一个URL（没有空格和其他文字）
    if text.startswith(('http://', 'https://')) and ' ' not in text and '\n' not in text:
        return text
    
    # 使用正则表达式提取所有URL
    # 支持http和https协议
    url_pattern = r'https?://[^\s\u4e00-\u9fa5<>"{}|\\^`\[\]]+(?:[^\s\u4e00-\u9fa5<>"{}|\\^`\[\].,;!?])'
    urls = re.findall(url_pattern, text)
    
    if not urls:
        # 尝试更宽松的匹配
        urls = re.findall(r'https?://[^\s]+', text)
    
    if not urls:
        logger.warning(f"未能从文本中提取URL: {text[:100]}")
        return None
    
    # 返回第一个URL并清理
    first_url = urls[0].strip()
    
    # 清理URL末尾可能的标点符号
    while first_url and first_url[-1] in '.,;!?)]}、。，；！？」】':
        first_url = first_url[:-1]
    
    logger.info(f"成功提取URL: {first_url}")
    return first_url


def extract_all_urls(text: str) -> list:
    """
    从文本中提取所有URL
    
    Args:
        text: 用户输入的文本
        
    Returns:
        URL列表
    """
    if not text or not isinstance(text, str):
        return []
    
    url_pattern = r'https?://[^\s\u4e00-\u9fa5<>"{}|\\^`\[\]]+(?:[^\s\u4e00-\u9fa5<>"{}|\\^`\[\].,;!?])'
    urls = re.findall(url_pattern, text)
    
    # 清理URL
    cleaned_urls = []
    for url in urls:
        url = url.strip()
        while url and url[-1] in '.,;!?)]}、。，；！？」】':
            url = url[:-1]
        if url:
            cleaned_urls.append(url)
    
    return cleaned_urls


def is_valid_url(url: str) -> bool:
    """
    验证URL是否有效
    
    Args:
        url: URL字符串
        
    Returns:
        是否是有效的URL
    """
    if not url or not isinstance(url, str):
        return False
    
    # 基本的URL格式验证
    url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
    return bool(re.match(url_pattern, url))


# 常见视频平台的URL模式
VIDEO_PLATFORM_PATTERNS = {
    'douyin': r'v\.douyin\.com|www\.douyin\.com',
    'kuaishou': r'v\.kuaishou\.com|www\.kuaishou\.com',
    'bilibili': r'www\.bilibili\.com|b23\.tv',
    'weixin': r'mp\.weixin\.qq\.com',
    'youtube': r'www\.youtube\.com|youtu\.be',
    'tiktok': r'www\.tiktok\.com|vm\.tiktok\.com',
    'xiaohongshu': r'xhslink\.com|www\.xiaohongshu\.com',
    'baidu': r'mr\.baidu\.com|pan\.baidu\.com',
}


def detect_platform(url: str) -> Optional[str]:
    """
    检测URL所属的视频平台
    
    Args:
        url: URL字符串
        
    Returns:
        平台名称或None
    """
    for platform, pattern in VIDEO_PLATFORM_PATTERNS.items():
        if re.search(pattern, url, re.IGNORECASE):
            return platform
    return None

