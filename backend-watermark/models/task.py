"""任务数据模型"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"  # 等待处理
    DOWNLOADING = "downloading"  # 下载中
    PROCESSING = "processing"  # 处理中
    UPLOADING = "uploading"  # 上传中
    COMPLETED = "completed"  # 完成
    FAILED = "failed"  # 失败


class MediaType(str, Enum):
    """媒体类型枚举"""
    VIDEO = "video"
    IMAGE = "image"


class WatermarkMethod(str, Enum):
    """去水印方法枚举"""
    CROP = "crop"  # 裁剪
    BLUR = "blur"  # 模糊
    COVER = "cover"  # 覆盖
    INPAINT = "inpaint"  # 填充


class TaskCreate(BaseModel):
    """创建任务请求"""
    url: str = Field(..., description="视频或图片URL")
    media_type: MediaType = Field(..., description="媒体类型：video/image")
    method: WatermarkMethod = Field(WatermarkMethod.CROP, description="去水印方法")
    watermark_region: Optional[Dict[str, int]] = Field(
        None, 
        description="水印区域坐标 {x, y, width, height}"
    )
    user_id: Optional[str] = Field(None, description="用户ID")


class WatermarkTask(BaseModel):
    """水印任务模型"""
    task_id: str = Field(..., description="任务ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    url: str = Field(..., description="原始URL")
    media_type: MediaType = Field(..., description="媒体类型")
    method: WatermarkMethod = Field(..., description="去水印方法")
    watermark_region: Optional[Dict[str, int]] = Field(None, description="水印区域")
    status: TaskStatus = Field(TaskStatus.PENDING, description="任务状态")
    progress: int = Field(0, ge=0, le=100, description="处理进度（0-100）")
    result_url: Optional[str] = Field(None, description="处理结果URL")
    error_message: Optional[str] = Field(None, description="错误信息")
    metadata: Optional[Dict[str, Any]] = Field(None, description="媒体元数据")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None, description="完成时间")


class TaskResponse(BaseModel):
    """任务响应"""
    task_id: str = Field(..., description="任务ID")
    status: TaskStatus = Field(..., description="任务状态")
    progress: int = Field(..., description="处理进度")
    result_url: Optional[str] = Field(None, description="结果URL")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ProcessHistory(BaseModel):
    """处理历史记录"""
    history_id: str = Field(..., description="历史记录ID")
    user_id: str = Field(..., description="用户ID")
    task_id: str = Field(..., description="任务ID")
    original_url: str = Field(..., description="原始URL")
    result_url: str = Field(..., description="结果URL")
    media_type: MediaType = Field(..., description="媒体类型")
    method: WatermarkMethod = Field(..., description="使用的方法")
    process_time: float = Field(..., description="处理耗时（秒）")
    file_size: int = Field(..., description="文件大小（字节）")
    created_at: datetime = Field(default_factory=datetime.now)


class TaskListResponse(BaseModel):
    """任务列表响应"""
    total: int = Field(..., description="总数")
    tasks: list[TaskResponse] = Field(..., description="任务列表")


class HistoryListResponse(BaseModel):
    """历史记录列表响应"""
    total: int = Field(..., description="总数")
    history: list[ProcessHistory] = Field(..., description="历史记录列表")


