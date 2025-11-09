"""任务管理API"""
from fastapi import APIRouter, HTTPException, Query
from backend_watermark.models.task import (
    TaskCreate,
    TaskResponse,
    TaskListResponse,
    TaskStatus
)
from backend_watermark.core.mongodb import get_mongodb
from backend_watermark.core.redis_client import get_redis
from backend_watermark.celery_app.tasks import process_watermark_task
from backend_watermark.utils.url_extractor import extract_url, is_valid_url
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/tasks", response_model=TaskResponse)
async def create_task(task: TaskCreate):
    """
    创建去水印任务
    
    - **url**: 视频或图片URL（支持从复制的文本中自动提取URL）
    - **media_type**: 媒体类型（video/image）
    - **method**: 去水印方法（crop/blur/cover/inpaint）
    - **watermark_region**: 水印区域坐标（可选）
    - **user_id**: 用户ID（可选）
    """
    try:
        # 从输入文本中提取URL
        extracted_url = extract_url(task.url)
        
        if not extracted_url:
            raise HTTPException(
                status_code=400, 
                detail="无法从输入文本中提取有效的URL，请确保包含完整的http://或https://链接"
            )
        
        # 验证URL格式
        if not is_valid_url(extracted_url):
            raise HTTPException(
                status_code=400,
                detail=f"提取的URL格式无效: {extracted_url}"
            )
        
        logger.info(f"提取的URL: {extracted_url}")
        
        # 生成任务ID
        task_id = str(uuid.uuid4())
        
        # 创建任务记录
        task_data = {
            "task_id": task_id,
            "user_id": task.user_id,
            "url": extracted_url,  # 使用提取后的URL
            "original_input": task.url,  # 保存原始输入
            "media_type": task.media_type.value,
            "method": task.method.value,
            "watermark_region": task.watermark_region,
            "status": TaskStatus.PENDING.value,
            "progress": 0,
            "result_url": None,
            "error_message": None,
            "metadata": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "completed_at": None
        }
        
        # 存入MongoDB
        db = get_mongodb()
        collection = db.get_collection("watermark_tasks")
        result = collection.insert_one(task_data)
        
        # 缓存到Redis（快速查询，排除MongoDB的_id）
        redis = get_redis()
        cache_data = {k: v for k, v in task_data.items() if k != '_id'}
        redis.set(f"task:{task_id}", cache_data, expire=3600 * 24)  # 24小时过期
        
        # 提交Celery任务
        process_watermark_task.delay(task_id)
        
        logger.info(f"任务创建成功: {task_id}")
        
        return TaskResponse(
            task_id=task_id,
            status=TaskStatus.PENDING,
            progress=0,
            result_url=None,
            error_message=None,
            created_at=task_data["created_at"],
            updated_at=task_data["updated_at"]
        )
        
    except Exception as e:
        logger.error(f"创建任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task_status(task_id: str):
    """
    查询任务状态
    
    - **task_id**: 任务ID
    """
    try:
        # 先从Redis查询
        redis = get_redis()
        task_data = redis.get(f"task:{task_id}")
        
        if not task_data:
            # Redis中没有，从MongoDB查询
            db = get_mongodb()
            collection = db.get_collection("watermark_tasks")
            task_data = collection.find_one({"task_id": task_id}, {"_id": 0})
            
            if not task_data:
                raise HTTPException(status_code=404, detail="任务不存在")
            
            # 更新Redis缓存
            redis.set(f"task:{task_id}", task_data, expire=3600 * 24)
        
        return TaskResponse(
            task_id=task_data["task_id"],
            status=TaskStatus(task_data["status"]),
            progress=task_data["progress"],
            result_url=task_data.get("result_url"),
            error_message=task_data.get("error_message"),
            created_at=task_data["created_at"],
            updated_at=task_data["updated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"查询任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询任务失败: {str(e)}")


@router.get("/tasks", response_model=TaskListResponse)
async def list_tasks(
    user_id: str = Query(None, description="用户ID"),
    status: TaskStatus = Query(None, description="任务状态"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    skip: int = Query(0, ge=0, description="跳过数量")
):
    """
    查询任务列表
    
    - **user_id**: 用户ID（可选）
    - **status**: 任务状态（可选）
    - **limit**: 每页数量
    - **skip**: 跳过数量
    """
    try:
        db = get_mongodb()
        collection = db.get_collection("watermark_tasks")
        
        # 构建查询条件
        query = {}
        if user_id:
            query["user_id"] = user_id
        if status:
            query["status"] = status.value
        
        # 查询总数
        total = collection.count_documents(query)
        
        # 查询任务列表
        tasks = list(collection.find(
            query,
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit))
        
        return TaskListResponse(
            total=total,
            tasks=[
                TaskResponse(
                    task_id=task["task_id"],
                    status=TaskStatus(task["status"]),
                    progress=task["progress"],
                    result_url=task.get("result_url"),
                    error_message=task.get("error_message"),
                    created_at=task["created_at"],
                    updated_at=task["updated_at"]
                )
                for task in tasks
            ]
        )
        
    except Exception as e:
        logger.error(f"查询任务列表失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询任务列表失败: {str(e)}")


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    删除任务
    
    - **task_id**: 任务ID
    """
    try:
        db = get_mongodb()
        collection = db.get_collection("watermark_tasks")
        
        result = collection.delete_one({"task_id": task_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        # 删除Redis缓存
        redis = get_redis()
        redis.delete(f"task:{task_id}")
        
        logger.info(f"任务删除成功: {task_id}")
        
        return {"message": "任务删除成功", "task_id": task_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除任务失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除任务失败: {str(e)}")


