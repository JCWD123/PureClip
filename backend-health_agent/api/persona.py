"""人物风格API"""
from fastapi import APIRouter, HTTPException
from backend.utils.persona_styles import get_all_persona_styles, PERSONA_STYLES
from backend.core.mongodb import get_mongodb
from backend.config.config import settings
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/persona-styles", summary="获取所有人物风格")
async def get_persona_styles():
    """获取所有可用的人物风格"""
    try:
        styles = get_all_persona_styles()
        return {"status": "success", "data": styles}
    except Exception as e:
        logger.error(f"获取人物风格失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/persona-styles/{style_name}", summary="获取指定人物风格详情")
async def get_persona_style_detail(style_name: str):
    """获取指定人物风格的详细信息"""
    try:
        style_info = PERSONA_STYLES.get(style_name)
        if not style_info:
            raise HTTPException(status_code=404, detail="人物风格不存在")
        
        return {
            "status": "success",
            "data": {
                "style_name": style_name,
                **style_info
            }
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取人物风格详情失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/persona-styles/{user_id}/select", summary="选择人物风格")
async def select_persona_style(user_id: str, style_name: str):
    """用户选择人物风格"""
    try:
        # 检查风格是否存在
        if style_name not in PERSONA_STYLES:
            raise HTTPException(status_code=400, detail="不支持的人物风格")
        
        # 检查用户是否已填写档案
        db = get_mongodb()
        collection = db.get_collection(settings.COLLECTION_HEALTH_PROFILE)
        profile = collection.find_one({"user_id": user_id})
        
        if not profile:
            raise HTTPException(status_code=400, detail="请先完成健康档案填写")
        
        # 更新人物风格
        result = collection.update_one(
            {"user_id": user_id},
            {"$set": {"persona_style": style_name, "updated_at": datetime.now()}}
        )
        
        logger.info(f"用户{user_id}选择人物风格：{style_name}")
        return {
            "status": "success",
            "message": f"成功选择'{style_name}'风格"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"选择人物风格失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/persona-styles/{user_id}/current", summary="获取用户当前人物风格")
async def get_current_persona_style(user_id: str):
    """获取用户当前选择的人物风格"""
    try:
        db = get_mongodb()
        collection = db.get_collection(settings.COLLECTION_HEALTH_PROFILE)
        profile = collection.find_one({"user_id": user_id})
        
        if not profile:
            raise HTTPException(status_code=404, detail="用户档案不存在")
        
        style_name = profile.get("persona_style")
        if not style_name:
            return {
                "status": "success",
                "data": None,
                "message": "用户尚未选择人物风格"
            }
        
        style_info = PERSONA_STYLES.get(style_name, {})
        return {
            "status": "success",
            "data": {
                "style_name": style_name,
                **style_info
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取当前人物风格失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))






