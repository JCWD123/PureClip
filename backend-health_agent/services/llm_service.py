"""阿里云百炼大模型服务"""
import requests
import logging
from backend.config.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """大模型调用服务"""
    
    def __init__(self):
        self.api_url = settings.DASHSCOPE_URL
        self.api_key = settings.DASHSCOPE_API_KEY
        self.model = settings.DASHSCOPE_MODEL
    
    def chat(self, messages: list, temperature: float = 2, max_tokens: int = 2000) -> str:
        """
        调用大模型生成回复
        
        Args:
            messages: 消息列表，格式 [{"role": "system/user/assistant", "content": "..."}]
            temperature: 温度参数，控制随机性
            max_tokens: 最大生成token数
            
        Returns:
            生成的文本内容
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            return content
            
        except Exception as e:
            logger.error(f"调用大模型失败: {e}")
            return f"抱歉，生成内容时出现错误：{str(e)}"
    
    def generate_rest_reminder(self, user_profile: dict, persona_prompt: str, time_type: str) -> str:
        """
        生成作息提醒
        
        Args:
            user_profile: 用户健康档案
            persona_prompt: 人物风格提示词
            time_type: 时间类型：morning/noon/night
        """
        basic_info = user_profile.get("basic_info", {})
        health_info = user_profile.get("health_info", {})
        
        time_desc = {
            "morning": "早上7点，该起床了",
            "noon": "中午1点，该午休了",
            "night": "晚上11点，该睡觉了"
        }
        
        messages = [
            {"role": "system", "content": persona_prompt},
            {"role": "user", "content": f"""
现在是{time_desc.get(time_type, "提醒时间")}。
用户信息：
- 姓名：{basic_info.get('nickname', '用户')}
- 年龄：{basic_info.get('age', '未知')}岁
- 生活习惯：{', '.join(health_info.get('lifestyle_habits', ['无特殊']))}

请生成一条温馨的作息提醒，100字以内，提醒用户按时作息的重要性。
"""}
        ]
        
        return self.chat(messages, temperature=0.8, max_tokens=200)
    
    def generate_meal_reminder(self, user_profile: dict, persona_prompt: str, meal_type: str) -> str:
        """
        生成饮食提醒
        
        Args:
            user_profile: 用户健康档案
            persona_prompt: 人物风格提示词
            meal_type: 餐次类型：breakfast/lunch/dinner
        """
        basic_info = user_profile.get("basic_info", {})
        health_info = user_profile.get("health_info", {})
        other_info = user_profile.get("other_info", {})
        
        meal_desc = {
            "breakfast": "早餐",
            "lunch": "午餐",
            "dinner": "晚餐"
        }
        
        # 获取所有健康信息
        allergies = health_info.get('allergies', [])
        medical_history = health_info.get('medical_history', [])
        lifestyle_habits = health_info.get('lifestyle_habits', [])
        adverse_reactions = health_info.get('adverse_reactions', [])
        family_history = health_info.get('family_history', [])
        
        messages = [
            {"role": "system", "content": persona_prompt},
            {"role": "user", "content": f"""
现在是{meal_desc.get(meal_type, '用餐')}时间。

用户基本信息：
- 姓名：{basic_info.get('nickname', '用户')}
- 年龄：{basic_info.get('age', '未知')}岁
- 性别：{basic_info.get('gender', '未知')}
- 身高：{basic_info.get('height', '未知')}cm
- 体重：{basic_info.get('weight', '未知')}kg
- 血型：{basic_info.get('blood_type', '未知')}

用户健康信息：
- 生活习惯：{', '.join(lifestyle_habits) if lifestyle_habits else '无特殊'}
- 过敏史：{', '.join(allergies) if allergies else '无'}
- 既往病史：{', '.join(medical_history) if medical_history else '无'}
- 药品不良反应：{', '.join(adverse_reactions) if adverse_reactions else '无'}
- 家族史：{', '.join(family_history) if family_history else '无'}

其他信息：
- 备注：{other_info.get('other_notes', '无')}

请根据用户的完整健康状况，生成一条饮食建议，包括：
1. 推荐的食物搭配
2. 需要避免的食物
3. 温馨提示
字数控制在150字以内。
"""}
        ]
        
        return self.chat(messages, temperature=0.7, max_tokens=300)
    
    def generate_weather_reminder(self, user_profile: dict, persona_prompt: str, weather_info: dict) -> str:
        """
        生成天气推送
        
        Args:
            user_profile: 用户健康档案
            persona_prompt: 人物风格提示词
            weather_info: 天气信息
        """
        basic_info = user_profile.get("basic_info", {})
        health_info = user_profile.get("health_info", {})
        other_info = user_profile.get("other_info", {})
        
        messages = [
            {"role": "system", "content": persona_prompt},
            {"role": "user", "content": f"""
今日天气情况：
- 温度：{weather_info.get('temperature', '未知')}
- 天气：{weather_info.get('weather', '未知')}
- 风力：{weather_info.get('wind', '未知')}

用户基本信息：
- 姓名：{basic_info.get('nickname', '用户')}
- 年龄：{basic_info.get('age', '未知')}岁
- 性别：{basic_info.get('gender', '未知')}

用户健康信息：
- 生活习惯：{', '.join(health_info.get('lifestyle_habits', ['无特殊']))}
- 过敏史：{', '.join(health_info.get('allergies', ['无']))}
- 既往病史：{', '.join(health_info.get('medical_history', ['无']))}
- 家族史：{', '.join(health_info.get('family_history', ['无']))}

其他信息：
- 备注：{other_info.get('other_notes', '无')}

请根据天气情况和用户的完整健康状况，生成一条温馨的天气提醒和健康建议，100字以内。
"""}
        ]
        
        return self.chat(messages, temperature=0.7, max_tokens=200)
    
    def generate_health_tip(self, user_profile: dict, persona_prompt: str) -> str:
        """
        生成养生妙招
        
        Args:
            user_profile: 用户健康档案
            persona_prompt: 人物风格提示词
        """
        basic_info = user_profile.get("basic_info", {})
        health_info = user_profile.get("health_info", {})
        other_info = user_profile.get("other_info", {})
        
        messages = [
            {"role": "system", "content": persona_prompt},
            {"role": "user", "content": f"""
用户基本信息：
- 姓名：{basic_info.get('nickname', '用户')}
- 年龄：{basic_info.get('age', '未知')}岁
- 性别：{basic_info.get('gender', '未知')}
- 身高：{basic_info.get('height', '未知')}cm
- 体重：{basic_info.get('weight', '未知')}kg
- 血型：{basic_info.get('blood_type', '未知')}

用户健康信息：
- 生活习惯：{', '.join(health_info.get('lifestyle_habits', ['无特殊']))}
- 过敏史：{', '.join(health_info.get('allergies', ['无']))}
- 既往病史：{', '.join(health_info.get('medical_history', ['无']))}
- 药品不良反应：{', '.join(health_info.get('adverse_reactions', ['无']))}
- 家族史：{', '.join(health_info.get('family_history', ['无']))}
- 手术史：{', '.join([f"{s.get('name', '')}({s.get('date', '')})" for s in health_info.get('surgery_history', [])]) if health_info.get('surgery_history') else '无'}

其他信息：
- 备注：{other_info.get('other_notes', '无')}

请根据用户的完整健康档案，生成一条实用的养生小妙招，要求：
1. 针对用户的实际情况
2. 简单易行
3. 科学有效
字数控制在150字以内。
"""}
        ]
        
        return self.chat(messages, temperature=0.8, max_tokens=300)


# 全局LLM服务实例
llm_service = LLMService()


