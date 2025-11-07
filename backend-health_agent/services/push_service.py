"""健康推送服务"""
import logging
from datetime import datetime
from backend.core.mongodb import get_mongodb
from backend.config.config import settings
from backend.services.llm_service import llm_service
from backend.utils.weather_crawler import weather_crawler
from backend.utils.persona_styles import get_persona_prompt

logger = logging.getLogger(__name__)


class PushService:
    """健康推送服务类"""
    
    def __init__(self):
        self.db = get_mongodb()
    
    def _get_user_profile(self, user_id: str) -> dict:
        """获取用户健康档案"""
        collection = self.db.get_collection(settings.COLLECTION_HEALTH_PROFILE)
        profile = collection.find_one({"user_id": user_id})
        return profile if profile else {}
    
    def _save_push_history(self, user_id: str, push_type: str, content: str):
        """保存推送历史"""
        collection = self.db.get_collection(settings.COLLECTION_PUSH_HISTORY)
        push_record = {
            "user_id": user_id,
            "push_type": push_type,
            "content": content,
            "push_time": datetime.now(),
            "is_read": False
        }
        collection.insert_one(push_record)
        logger.info(f"保存推送历史：用户{user_id}，类型{push_type}")
    
    def push_rest_reminder(self, user_id: str, time_type: str) -> dict:
        """
        推送作息提醒
        
        Args:
            user_id: 用户ID
            time_type: 时间类型 morning/noon/night
        """
        try:
            # 获取用户档案
            profile = self._get_user_profile(user_id)
            if not profile:
                return {"status": "error", "message": "用户档案不存在"}
            
            # 获取人物风格
            persona_style = profile.get("persona_style", "专业顾问")
            persona_prompt = get_persona_prompt(persona_style)
            
            # 生成提醒内容
            content = llm_service.generate_rest_reminder(profile, persona_prompt, time_type)
            
            # 保存推送历史
            self._save_push_history(user_id, "rest", content)
            
            return {
                "status": "success",
                "content": content,
                "push_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"推送作息提醒失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def push_meal_reminder(self, user_id: str, meal_type: str) -> dict:
        """
        推送饮食提醒
        
        Args:
            user_id: 用户ID
            meal_type: 餐次类型 breakfast/lunch/dinner
        """
        try:
            profile = self._get_user_profile(user_id)
            if not profile:
                return {"status": "error", "message": "用户档案不存在"}
            
            persona_style = profile.get("persona_style", "专业顾问")
            persona_prompt = get_persona_prompt(persona_style)
            
            content = llm_service.generate_meal_reminder(profile, persona_prompt, meal_type)
            self._save_push_history(user_id, "meal", content)
            
            return {
                "status": "success",
                "content": content,
                "push_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"推送饮食提醒失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def push_weather_reminder(self, user_id: str) -> dict:
        """推送天气提醒"""
        try:
            profile = self._get_user_profile(user_id)
            if not profile:
                return {"status": "error", "message": "用户档案不存在"}
            
            # 获取用户所在地区
            location = profile.get("location")
            if not location:
                return {"status": "error", "message": "用户未设置所在地区"}
            
            province = location.get("province", "浙江")
            city = location.get("city", "杭州")
            
            # 爬取天气信息
            weather_info = weather_crawler.crawl_weather(province, city)
            
            # 检查是否爬取失败
            if "error" in weather_info:
                return {"status": "error", "message": weather_info["error"]}
            
            # 获取人物风格
            persona_style = profile.get("persona_style", "专业顾问")
            persona_prompt = get_persona_prompt(persona_style)
            
            # 生成推送内容
            content = llm_service.generate_weather_reminder(profile, persona_prompt, weather_info)
            
            # 合并天气信息和建议
            full_content = f"【今日天气】\n{weather_info['city']} {weather_info['weather']} {weather_info['temperature']}\n{weather_info['wind']}\n\n{content}"
            
            self._save_push_history(user_id, "weather", full_content)
            
            return {
                "status": "success",
                "content": full_content,
                "weather_info": weather_info,
                "push_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"推送天气提醒失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def push_health_tip(self, user_id: str) -> dict:
        """推送养生妙招"""
        try:
            profile = self._get_user_profile(user_id)
            if not profile:
                return {"status": "error", "message": "用户档案不存在"}
            
            persona_style = profile.get("persona_style", "专业顾问")
            persona_prompt = get_persona_prompt(persona_style)
            
            content = llm_service.generate_health_tip(profile, persona_prompt)
            self._save_push_history(user_id, "health_tip", content)
            
            return {
                "status": "success",
                "content": content,
                "push_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"推送养生妙招失败: {e}")
            return {"status": "error", "message": str(e)}
    
    def get_push_history(self, user_id: str, push_type: str = None, limit: int = 20) -> list:
        """
        获取推送历史
        
        Args:
            user_id: 用户ID
            push_type: 推送类型，不指定则获取所有类型
            limit: 返回数量限制
        """
        try:
            collection = self.db.get_collection(settings.COLLECTION_PUSH_HISTORY)
            
            query = {"user_id": user_id}
            if push_type:
                query["push_type"] = push_type
            
            cursor = collection.find(query).sort("push_time", -1).limit(limit)
            
            history = []
            for record in cursor:
                record["_id"] = str(record["_id"])
                history.append(record)
            
            return history
            
        except Exception as e:
            logger.error(f"获取推送历史失败: {e}")
            return []
    
    def mark_as_read(self, user_id: str, push_id: str) -> bool:
        """标记推送为已读"""
        try:
            from bson.objectid import ObjectId
            collection = self.db.get_collection(settings.COLLECTION_PUSH_HISTORY)
            
            result = collection.update_one(
                {"_id": ObjectId(push_id), "user_id": user_id},
                {"$set": {"is_read": True}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"标记已读失败: {e}")
            return False


# 全局推送服务实例
push_service = PushService()


