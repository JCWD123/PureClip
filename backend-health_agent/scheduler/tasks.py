"""定时任务"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from backend.config.config import settings
from backend.services.push_service import push_service
from backend.core.mongodb import get_mongodb

logger = logging.getLogger(__name__)


class HealthScheduler:
    """健康推送定时任务调度器"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone=settings.SCHEDULER_TIMEZONE)
        self.db = get_mongodb()
    
    def _get_all_users(self) -> list:
        """获取所有用户ID"""
        try:
            collection = self.db.get_collection(settings.COLLECTION_HEALTH_PROFILE)
            users = collection.find({}, {"user_id": 1})
            return [user["user_id"] for user in users]
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            return []
    
    async def rest_reminder_task(self, time_type: str):
        """作息提醒任务"""
        logger.info(f"开始执行作息提醒任务：{time_type}")
        users = self._get_all_users()
        
        for user_id in users:
            try:
                push_service.push_rest_reminder(user_id, time_type)
            except Exception as e:
                logger.error(f"用户{user_id}作息提醒推送失败: {e}")
    
    async def meal_reminder_task(self, meal_type: str):
        """饮食提醒任务"""
        logger.info(f"开始执行饮食提醒任务：{meal_type}")
        users = self._get_all_users()
        
        for user_id in users:
            try:
                push_service.push_meal_reminder(user_id, meal_type)
            except Exception as e:
                logger.error(f"用户{user_id}饮食提醒推送失败: {e}")
    
    async def weather_reminder_task(self):
        """天气提醒任务"""
        logger.info("开始执行天气提醒任务")
        users = self._get_all_users()
        
        for user_id in users:
            try:
                # 只为设置了地区的用户推送
                collection = self.db.get_collection(settings.COLLECTION_HEALTH_PROFILE)
                profile = collection.find_one({"user_id": user_id})
                
                if profile and profile.get("location"):
                    push_service.push_weather_reminder(user_id)
            except Exception as e:
                logger.error(f"用户{user_id}天气提醒推送失败: {e}")
    
    async def health_tip_task(self):
        """养生妙招任务"""
        logger.info("开始执行养生妙招任务")
        users = self._get_all_users()
        
        for user_id in users:
            try:
                push_service.push_health_tip(user_id)
            except Exception as e:
                logger.error(f"用户{user_id}养生妙招推送失败: {e}")
    
    def start(self):
        """启动定时任务"""
        # 作息提醒任务
        for time_str in settings.REST_TIMES:
            hour, minute = time_str.split(":")
            time_type_map = {"07:00": "morning", "13:00": "noon", "23:00": "night"}
            time_type = time_type_map.get(time_str, "morning")
            
            self.scheduler.add_job(
                self.rest_reminder_task,
                CronTrigger(hour=int(hour), minute=int(minute)),
                args=[time_type],
                id=f"rest_reminder_{time_str}",
                name=f"作息提醒-{time_str}"
            )
            logger.info(f"已添加作息提醒任务：{time_str}")
        
        # 饮食提醒任务
        meal_time_map = {
            "07:30": "breakfast",
            "12:00": "lunch",
            "18:00": "dinner"
        }
        for time_str in settings.MEAL_TIMES:
            hour, minute = time_str.split(":")
            meal_type = meal_time_map.get(time_str, "lunch")
            
            self.scheduler.add_job(
                self.meal_reminder_task,
                CronTrigger(hour=int(hour), minute=int(minute)),
                args=[meal_type],
                id=f"meal_reminder_{time_str}",
                name=f"饮食提醒-{time_str}"
            )
            logger.info(f"已添加饮食提醒任务：{time_str}")
        
        # 天气提醒任务
        weather_hour, weather_minute = settings.WEATHER_TIME.split(":")
        self.scheduler.add_job(
            self.weather_reminder_task,
            CronTrigger(hour=int(weather_hour), minute=int(weather_minute)),
            id="weather_reminder",
            name="天气提醒"
        )
        logger.info(f"已添加天气提醒任务：{settings.WEATHER_TIME}")
        
        # 养生妙招任务
        health_hour, health_minute = settings.HEALTH_TIP_TIME.split(":")
        self.scheduler.add_job(
            self.health_tip_task,
            CronTrigger(hour=int(health_hour), minute=int(health_minute)),
            id="health_tip",
            name="养生妙招"
        )
        logger.info(f"已添加养生妙招任务：{settings.HEALTH_TIP_TIME}")
        
        # 启动调度器
        self.scheduler.start()
        logger.info("定时任务调度器已启动")
    
    def shutdown(self):
        """关闭调度器"""
        self.scheduler.shutdown()
        logger.info("定时任务调度器已关闭")


# 全局调度器实例
health_scheduler = HealthScheduler()






