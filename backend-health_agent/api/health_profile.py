"""健康档案管理API"""
from fastapi import APIRouter, HTTPException, Body
from datetime import datetime
from backend.models.health_profile import (
    HealthProfile, HealthProfileCreate, HealthProfileUpdate
)
from backend.core.mongodb import get_mongodb
from backend.config.config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/health-profile", summary="创建健康档案")
async def create_health_profile(profile: HealthProfileCreate):
    """创建用户健康档案"""
    try:
        db = get_mongodb()
        collection = db.get_collection(settings.COLLECTION_HEALTH_PROFILE)
        
        # 检查用户是否已有档案
        existing = collection.find_one({"user_id": profile.user_id})
        if existing:
            raise HTTPException(status_code=400, detail="该用户已存在健康档案")
        
        # 创建档案
        profile_dict = {
            "user_id": profile.user_id,
            "basic_info": profile.basic_info.dict(),
            "health_info": profile.health_info.dict(),
            "other_info": profile.other_info.dict(),
            "persona_style": None,
            "location": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        result = collection.insert_one(profile_dict)
        profile_dict["_id"] = str(result.inserted_id)
        
        logger.info(f"创建健康档案成功：用户{profile.user_id}")
        return {"status": "success", "message": "健康档案创建成功", "data": profile_dict}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"创建健康档案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-profile/{user_id}", summary="获取健康档案")
async def get_health_profile(user_id: str):
    """获取用户健康档案"""
    try:
        db = get_mongodb()
        collection = db.get_collection(settings.COLLECTION_HEALTH_PROFILE)
        
        profile = collection.find_one({"user_id": user_id})
        if not profile:
            raise HTTPException(status_code=404, detail="健康档案不存在")
        
        profile["_id"] = str(profile["_id"])
        return {"status": "success", "data": profile}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取健康档案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/health-profile/{user_id}", summary="更新健康档案")
async def update_health_profile(user_id: str, update_data: HealthProfileUpdate):
    """更新用户健康档案"""
    try:
        db = get_mongodb()
        collection = db.get_collection(settings.COLLECTION_HEALTH_PROFILE)
        
        # 构建更新数据
        update_dict = {}
        if update_data.basic_info:
            update_dict["basic_info"] = update_data.basic_info.dict()
        if update_data.health_info:
            update_dict["health_info"] = update_data.health_info.dict()
        if update_data.other_info:
            update_dict["other_info"] = update_data.other_info.dict()
        if update_data.persona_style:
            update_dict["persona_style"] = update_data.persona_style
        if update_data.location:
            update_dict["location"] = update_data.location
        
        update_dict["updated_at"] = datetime.now()
        
        result = collection.update_one(
            {"user_id": user_id},
            {"$set": update_dict}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="健康档案不存在")
        
        logger.info(f"更新健康档案成功：用户{user_id}")
        return {"status": "success", "message": "健康档案更新成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新健康档案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/health-profile/{user_id}", summary="删除健康档案")
async def delete_health_profile(user_id: str):
    """删除用户健康档案"""
    try:
        db = get_mongodb()
        collection = db.get_collection(settings.COLLECTION_HEALTH_PROFILE)
        
        result = collection.delete_one({"user_id": user_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="健康档案不存在")
        
        logger.info(f"删除健康档案成功：用户{user_id}")
        return {"status": "success", "message": "健康档案删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"删除健康档案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health-profile/{user_id}/location", summary="设置用户地区")
async def set_user_location(
    user_id: str,
    location: dict = Body(..., examples=[{"province": "浙江", "city": "杭州"}])
):
    """设置用户所在地区（用于天气推送）"""
    try:
        db = get_mongodb()
        collection = db.get_collection(settings.COLLECTION_HEALTH_PROFILE)
        
        result = collection.update_one(
            {"user_id": user_id},
            {"$set": {"location": location, "updated_at": datetime.now()}}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="健康档案不存在")
        
        logger.info(f"设置用户地区成功：用户{user_id}")
        return {"status": "success", "message": "地区设置成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"设置用户地区失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))





