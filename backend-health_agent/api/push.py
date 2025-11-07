"""健康推送API"""
from fastapi import APIRouter, HTTPException, Query
from backend.services.push_service import push_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/push/rest/{user_id}", summary="推送作息提醒")
async def push_rest_reminder(
    user_id: str,
    time_type: str = Query(..., description="时间类型：morning/noon/night")
):
    """手动触发作息提醒推送"""
    try:
        if time_type not in ["morning", "noon", "night"]:
            raise HTTPException(status_code=400, detail="time_type必须是morning/noon/night之一")
        
        result = push_service.push_rest_reminder(user_id, time_type)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推送作息提醒失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push/meal/{user_id}", summary="推送饮食提醒")
async def push_meal_reminder(
    user_id: str,
    meal_type: str = Query(..., description="餐次类型：breakfast/lunch/dinner")
):
    """手动触发饮食提醒推送"""
    try:
        if meal_type not in ["breakfast", "lunch", "dinner"]:
            raise HTTPException(status_code=400, detail="meal_type必须是breakfast/lunch/dinner之一")
        
        result = push_service.push_meal_reminder(user_id, meal_type)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推送饮食提醒失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push/weather/{user_id}", summary="推送天气提醒")
async def push_weather_reminder(user_id: str):
    """手动触发天气提醒推送"""
    try:
        result = push_service.push_weather_reminder(user_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推送天气提醒失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/push/health-tip/{user_id}", summary="推送养生妙招")
async def push_health_tip(user_id: str):
    """手动触发养生妙招推送"""
    try:
        result = push_service.push_health_tip(user_id)
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["message"])
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"推送养生妙招失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/push/history/{user_id}", summary="获取推送历史")
async def get_push_history(
    user_id: str,
    push_type: str = Query(None, description="推送类型：rest/meal/weather/health_tip，不指定则获取所有"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """获取用户的推送历史记录"""
    try:
        history = push_service.get_push_history(user_id, push_type, limit)
        return {
            "status": "success",
            "data": history,
            "count": len(history)
        }
        
    except Exception as e:
        logger.error(f"获取推送历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/push/history/{push_id}/read", summary="标记推送为已读")
async def mark_push_as_read(push_id: str, user_id: str = Query(...)):
    """标记某条推送为已读"""
    try:
        success = push_service.mark_as_read(user_id, push_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="推送记录不存在或已读")
        
        return {"status": "success", "message": "标记已读成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"标记已读失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))






