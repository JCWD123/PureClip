"""Celery异步任务"""
from celery import Task
from backend_watermark.celery_app.celery import celery_app
from backend_watermark.core.mongodb import get_mongodb
from backend_watermark.core.redis_client import get_redis
from backend_watermark.core.minio_client import get_minio
from backend_watermark.services.video_processor import VideoProcessor
from backend_watermark.services.image_processor import ImageProcessor
from backend_watermark.services.downloader import Downloader
from backend_watermark.models.task import TaskStatus, MediaType, WatermarkMethod
from datetime import datetime
import logging
import uuid
import os

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """带回调的任务基类"""
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """任务失败回调"""
        logger.error(f"任务失败: {task_id}, 错误: {exc}")


@celery_app.task(base=CallbackTask, bind=True)
def process_watermark_task(self, task_id: str):
    """
    处理去水印任务 - 轻量级模式（直接返回解析后的URL）
    
    Args:
        task_id: 任务ID
    """
    logger.info(f"开始处理任务: {task_id}")
    
    db = get_mongodb()
    redis = get_redis()
    collection = db.get_collection("watermark_tasks")
    
    try:
        # 获取任务信息
        task = collection.find_one({"task_id": task_id})
        if not task:
            raise Exception(f"任务不存在: {task_id}")
        
        # 更新任务状态：解析中
        update_task_status(task_id, TaskStatus.DOWNLOADING, 10, message="正在解析视频链接...")
        
        # 1. 解析视频链接（使用iiilab API）
        downloader = Downloader()
        from backend_watermark.services.video_parser import VideoParser
        parser = VideoParser()
        
        logger.info(f"开始解析链接: {task['url']}")
        parse_result = parser.parse(task["url"])
        
        if not parse_result['success']:
            raise Exception(f"链接解析失败: {parse_result.get('error', '未知错误')}")
        
        # 2. 获取真实视频URL（这个URL已经是无水印版本）
        result_url = parse_result['video_url']
        video_title = parse_result.get('title', '未知标题')
        video_cover = parse_result.get('cover')
        video_author = parse_result.get('author')
        
        logger.info(f"✅ 解析成功！")
        logger.info(f"   标题: {video_title}")
        logger.info(f"   视频URL: {result_url[:100]}...")
        
        # 更新任务状态：处理中（获取元数据）
        update_task_status(task_id, TaskStatus.PROCESSING, 50, message="正在获取视频信息...")
        
        # 3. 获取视频元数据（可选，用于前端显示）
        metadata = {
            'title': video_title,
            'cover': video_cover,
            'author': video_author,
            'platform': parse_result.get('platform', 'unknown')
        }
        
        # 4. 更新任务状态：完成
        update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            100,
            result_url=result_url,
            metadata=metadata,
            message="解析完成！"
        )
        
        # 5. 保存处理历史（简化版）
        save_parse_history(task, result_url, metadata)
        
        logger.info(f"✅ 任务处理完成: {task_id}")
        logger.info(f"✅ 返回URL: {result_url}")
        return {"task_id": task_id, "result_url": result_url, "metadata": metadata}
        
    except Exception as e:
        logger.error(f"任务处理失败: {task_id}, 错误: {e}")
        
        # 更新任务状态：失败
        update_task_status(
            task_id,
            TaskStatus.FAILED,
            error_message=str(e)
        )
        
        raise


def update_task_status(
    task_id: str,
    status: TaskStatus,
    progress: int = None,
    result_url: str = None,
    error_message: str = None,
    metadata: dict = None,
    message: str = None
):
    """
    更新任务状态
    
    Args:
        task_id: 任务ID
        status: 任务状态
        progress: 进度（0-100）
        result_url: 结果URL
        error_message: 错误信息
        metadata: 元数据（标题、封面等）
        message: 状态消息
    """
    db = get_mongodb()
    redis = get_redis()
    collection = db.get_collection("watermark_tasks")
    
    update_data = {
        "status": status.value,
        "updated_at": datetime.now()
    }
    
    if progress is not None:
        update_data["progress"] = progress
    
    if result_url:
        update_data["result_url"] = result_url
        update_data["completed_at"] = datetime.now()
    
    if error_message:
        update_data["error_message"] = error_message
    
    if metadata:
        update_data["metadata"] = metadata
    
    if message:
        update_data["message"] = message
    
    # 更新MongoDB
    collection.update_one(
        {"task_id": task_id},
        {"$set": update_data}
    )
    
    # 更新Redis缓存（排除_id字段）
    task = collection.find_one({"task_id": task_id}, {"_id": 0})
    if task:
        redis.set(f"task:{task_id}", task, expire=3600 * 24)
    
    logger.info(f"任务状态更新: {task_id} -> {status.value} ({message or ''})")


def save_process_history(task: dict, result_file: str, result_url: str):
    """
    保存处理历史记录
    
    Args:
        task: 任务信息
        result_file: 结果文件路径
        result_url: 结果URL
    """
    if not task.get("user_id"):
        return
    
    db = get_mongodb()
    collection = db.get_collection("process_history")
    
    # 计算处理耗时
    process_time = (datetime.now() - task["created_at"]).total_seconds()
    
    # 获取文件大小
    file_size = os.path.getsize(result_file)
    
    history = {
        "history_id": str(uuid.uuid4()),
        "user_id": task["user_id"],
        "task_id": task["task_id"],
        "original_url": task["url"],
        "result_url": result_url,
        "media_type": task["media_type"],
        "method": task["method"],
        "process_time": process_time,
        "file_size": file_size,
        "created_at": datetime.now()
    }
    
    collection.insert_one(history)
    logger.info(f"处理历史已保存: {history['history_id']}")


def save_parse_history(task: dict, result_url: str, metadata: dict):
    """
    保存解析历史记录（轻量级模式）
    
    Args:
        task: 任务信息
        result_url: 结果URL
        metadata: 视频元数据
    """
    if not task.get("user_id"):
        return
    
    db = get_mongodb()
    collection = db.get_collection("process_history")
    
    # 计算处理耗时
    process_time = (datetime.now() - task["created_at"]).total_seconds()
    
    history = {
        "history_id": str(uuid.uuid4()),
        "user_id": task["user_id"],
        "task_id": task["task_id"],
        "original_url": task.get("original_input", task["url"]),
        "result_url": result_url,
        "media_type": task["media_type"],
        "method": "parse",  # 标记为解析模式
        "process_time": process_time,
        "metadata": metadata,  # 保存元数据（标题、封面等）
        "created_at": datetime.now()
    }
    
    collection.insert_one(history)
    logger.info(f"解析历史已保存: {history['history_id']}")


def cleanup_files(files: list):
    """
    清理临时文件
    
    Args:
        files: 文件路径列表
    """
    for file in files:
        try:
            if file and os.path.exists(file):
                os.remove(file)
                logger.info(f"临时文件已删除: {file}")
        except Exception as e:
            logger.error(f"删除临时文件失败: {file}, 错误: {e}")


