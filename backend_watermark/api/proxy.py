"""
代理下载API
解决微信小程序 downloadFile 域名限制问题
"""

from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import StreamingResponse
import httpx
import logging
from typing import Optional

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/proxy/download")
async def proxy_download(
    url: str = Query(..., description="要下载的文件URL"),
    user_id: Optional[str] = Query(None, description="用户ID（用于统计）")
):
    """
    代理下载第三方资源
    
    功能:
    - 下载第三方CDN的视频/图片
    - 流式返回给前端
    - 解决微信小程序域名限制
    
    支持平台:
    - 百度: https://vd4.bdstatic.com/...
    - 抖音: https://aweme.snssdk.com/...
    - 快手: https://v.kuaishou.com/...
    - 小红书: https://sns-video-bd.xhscdn.com/...
    
    Args:
        url: 要下载的文件URL
        user_id: 用户ID（可选，用于统计）
        
    Returns:
        StreamingResponse: 流式返回文件内容
    """
    try:
        logger.info(f"📥 代理下载请求")
        logger.info(f"  URL: {url[:100]}{'...' if len(url) > 100 else ''}")
        if user_id:
            logger.info(f"  用户ID: {user_id}")
        
        # 验证URL
        if not url.startswith(('http://', 'https://')):
            logger.error(f"❌ 无效的URL: {url}")
            raise HTTPException(status_code=400, detail="无效的URL")
        
        # 获取文件信息（用于响应头）
        content_type = 'application/octet-stream'
        content_length = None
        
        try:
            # 创建临时客户端获取文件信息
            async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as temp_client:
                head_response = await temp_client.head(url)
                content_type = head_response.headers.get('content-type', 'application/octet-stream')
                content_length = head_response.headers.get('content-length')
                
                logger.info(f"✅ 文件信息获取成功")
                logger.info(f"  Content-Type: {content_type}")
                logger.info(f"  Content-Length: {content_length} bytes")
        except Exception as e:
            logger.warning(f"⚠️ HEAD请求失败，使用默认值: {e}")
        
        # ✅ 修复：在生成器内部创建 client，确保生命周期正确
        async def generate():
            """生成器函数，流式返回文件内容"""
            try:
                # 在生成器内部创建独立的 client
                async with httpx.AsyncClient(
                    timeout=120.0,
                    follow_redirects=True,
                    verify=True
                ) as client:
                    logger.info(f"📥 开始下载文件...")
                    
                    async with client.stream('GET', url) as response:
                        response.raise_for_status()
                        
                        total_size = 0
                        chunk_count = 0
                        async for chunk in response.aiter_bytes(chunk_size=8192):
                            total_size += len(chunk)
                            chunk_count += 1
                            yield chunk
                            
                            # 每传输 1MB 记录一次日志
                            if chunk_count % 128 == 0:  # 128 * 8KB = 1MB
                                logger.info(f"  已传输: {total_size / 1024 / 1024:.2f} MB")
                        
                        logger.info(f"✅ 下载完成，总大小: {total_size / 1024 / 1024:.2f} MB ({total_size} bytes)")
                        
            except httpx.HTTPStatusError as e:
                logger.error(f"❌ HTTP错误: {e.response.status_code}")
                raise
            except httpx.TimeoutException:
                logger.error(f"❌ 下载超时")
                raise
            except Exception as e:
                logger.error(f"❌ 下载错误: {str(e)}")
                raise
        
        # 构建响应头
        headers = {
            'Content-Type': content_type,
            'Content-Disposition': 'attachment',
            'Cache-Control': 'no-cache',
            'Access-Control-Allow-Origin': '*'
        }
        
        if content_length:
            headers['Content-Length'] = content_length
        
        logger.info(f"📤 返回流式响应")
        
        # 返回流式响应
        return StreamingResponse(
            generate(),
            headers=headers,
            media_type=content_type
        )
            
    except httpx.HTTPStatusError as e:
        logger.error(f"❌ 下载失败 - HTTP错误 {e.response.status_code}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"下载失败: HTTP {e.response.status_code}"
        )
    
    except httpx.TimeoutException:
        logger.error("❌ 下载超时")
        raise HTTPException(status_code=504, detail="下载超时，请稍后重试")
    
    except httpx.ConnectError:
        logger.error("❌ 连接失败")
        raise HTTPException(status_code=502, detail="无法连接到资源服务器")
    
    except Exception as e:
        logger.error(f"❌ 下载失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")
