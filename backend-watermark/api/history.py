"""历史记录API"""
from fastapi import APIRouter, HTTPException, Query
from backend_watermark.models.task import HistoryListResponse, ProcessHistory
from backend_watermark.core.mongodb import get_mongodb
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/history", response_model=HistoryListResponse)
async def get_history(
    user_id: str = Query(..., description="用户ID"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    skip: int = Query(0, ge=0, description="跳过数量")
):
    """
    获取用户处理历史记录
    
    - **user_id**: 用户ID
    - **limit**: 每页数量
    - **skip**: 跳过数量
    """
    try:
        db = get_mongodb()
        collection = db.get_collection("process_history")
        
        # 查询总数
        total = collection.count_documents({"user_id": user_id})
        
        # 查询历史记录
        history_list = list(collection.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("created_at", -1).skip(skip).limit(limit))
        
        return HistoryListResponse(
            total=total,
            history=[ProcessHistory(**h) for h in history_list]
        )
        
    except Exception as e:
        logger.error(f"查询历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"查询历史记录失败: {str(e)}")


@router.delete("/history/{history_id}")
async def delete_history(history_id: str):
    """
    删除历史记录
    
    - **history_id**: 历史记录ID
    """
    try:
        db = get_mongodb()
        collection = db.get_collection("process_history")
        
        result = collection.delete_one({"history_id": history_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="历史记录不存在")
        
        logger.info(f"历史记录删除成功: {history_id}")
        
        return {"message": "历史记录删除成功", "history_id": history_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除历史记录失败: {e}")
        raise HTTPException(status_code=500, detail=f"删除历史记录失败: {str(e)}")


