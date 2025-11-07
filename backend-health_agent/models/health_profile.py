"""健康档案数据模型"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BasicInfo(BaseModel):
    """基础信息"""
    nickname: str = Field(..., description="昵称")
    birth_date: str = Field(..., description="出生年月，格式：YYYY-MM")
    age: int = Field(..., ge=0, le=150, description="年龄")
    gender: str = Field(..., description="性别：男/女")
    height: float = Field(..., gt=0, description="身高（cm）")
    weight: float = Field(..., gt=0, description="体重（kg）")
    blood_type: Optional[str] = Field(None, description="血型：A/B/AB/O/未知")


class HealthInfo(BaseModel):
    """健康信息"""
    lifestyle_habits: List[str] = Field(default_factory=list, description="生活习惯，如：口味偏咸、久坐、熬夜等")
    allergies: List[str] = Field(default_factory=list, description="过敏史，如：青霉素过敏、鸡蛋过敏等")
    medical_history: List[str] = Field(default_factory=list, description="既往病史，如：乙肝、糖尿病等")
    adverse_reactions: List[str] = Field(default_factory=list, description="药品不良反应，如：服用阿莫西林后腹泻")
    family_history: List[str] = Field(default_factory=list, description="家族史，如：直系亲属患糖尿病")
    surgery_history: List[dict] = Field(default_factory=list, description="手术史，包含手术名称和时间")


class OtherInfo(BaseModel):
    """其他健康信息"""
    vaccination: List[dict] = Field(default_factory=list, description="疫苗接种记录")
    menstruation: Optional[dict] = Field(None, description="月经情况（女性）")
    fertility: Optional[dict] = Field(None, description="生育情况")
    other_notes: Optional[str] = Field(None, description="其他备注")


class HealthProfile(BaseModel):
    """完整健康档案"""
    user_id: str = Field(..., description="用户ID")
    basic_info: BasicInfo
    health_info: HealthInfo
    other_info: OtherInfo
    persona_style: Optional[str] = Field(None, description="选择的人物风格")
    location: Optional[dict] = Field(None, description="所在地区：{province: '', city: ''}")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class HealthProfileCreate(BaseModel):
    """创建健康档案请求"""
    user_id: str
    basic_info: BasicInfo
    health_info: HealthInfo
    other_info: OtherInfo


class HealthProfileUpdate(BaseModel):
    """更新健康档案请求"""
    basic_info: Optional[BasicInfo] = None
    health_info: Optional[HealthInfo] = None
    other_info: Optional[OtherInfo] = None
    persona_style: Optional[str] = None
    location: Optional[dict] = None


class PersonaStyle(BaseModel):
    """人物风格"""
    style_name: str = Field(..., description="风格名称")
    description: str = Field(..., description="风格描述")
    prompt: str = Field(..., description="对应的提示词")
    icon: Optional[str] = Field(None, description="图标")


class PushHistory(BaseModel):
    """推送历史记录"""
    user_id: str
    push_type: str = Field(..., description="推送类型：rest/meal/weather/health_tip")
    content: str = Field(..., description="推送内容")
    push_time: datetime = Field(default_factory=datetime.now)
    is_read: bool = Field(default=False, description="是否已读")






