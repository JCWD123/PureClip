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
    处理去水印任务
    
    Args:
        task_id: 任务ID
    """
    logger.info(f"开始处理任务: {task_id}")
    
    db = get_mongodb()
    redis = get_redis()
    minio = get_minio()
    collection = db.get_collection("watermark_tasks")
    
    try:
        # 获取任务信息
        task = collection.find_one({"task_id": task_id})
        if not task:
            raise Exception(f"任务不存在: {task_id}")
        
        # 更新任务状态：下载中
        update_task_status(task_id, TaskStatus.DOWNLOADING, 10)
        
        # 1. 下载原始文件
        downloader = Downloader()
        local_file = downloader.download(task["url"], task["media_type"])
        logger.info(f"文件下载完成: {local_file}")
        
        # 更新任务状态：处理中
        update_task_status(task_id, TaskStatus.PROCESSING, 30)
        
        # 2. 处理文件（去水印）
        if task["media_type"] == MediaType.VIDEO.value:
            processor = VideoProcessor()
            result_file = processor.remove_watermark(
                local_file,
                method=WatermarkMethod(task["method"]),
                region=task.get("watermark_region")
            )
        else:  # IMAGE
            processor = ImageProcessor()
            result_file = processor.remove_watermark(
                local_file,
                method=WatermarkMethod(task["method"]),
                region=task.get("watermark_region")
            )
        
        logger.info(f"文件处理完成: {result_file}")
        
        # 更新任务状态：上传中
        update_task_status(task_id, TaskStatus.UPLOADING, 70)
        
        # 3. 上传到MinIO
        object_name = f"{task['media_type']}/{task_id}/{os.path.basename(result_file)}"
        result_url = minio.upload_file(result_file, object_name)
        logger.info(f"文件上传完成: {result_url}")
        
        # 4. 更新任务状态：完成
        update_task_status(
            task_id,
            TaskStatus.COMPLETED,
            100,
            result_url=result_url
        )
        
        # 5. 保存处理历史
        save_process_history(task, result_file, result_url)
        
        # 6. 清理临时文件
        cleanup_files([local_file, result_file])
        
        logger.info(f"任务处理完成: {task_id}")
        return {"task_id": task_id, "result_url": result_url}
        
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
    error_message: str = None
):
    """
    更新任务状态
    
    Args:
        task_id: 任务ID
        status: 任务状态
        progress: 进度（0-100）
        result_url: 结果URL
        error_message: 错误信息
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
    
    # 更新MongoDB
    collection.update_one(
        {"task_id": task_id},
        {"$set": update_data}
    )
    
    # 更新Redis缓存
    task = collection.find_one({"task_id": task_id}, {"_id": 0})
    redis.set(f"task:{task_id}", task, expire=3600 * 24)
    
    logger.info(f"任务状态更新: {task_id} -> {status.value}")


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


