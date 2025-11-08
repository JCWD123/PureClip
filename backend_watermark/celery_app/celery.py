"""Celery应用配置"""
from celery import Celery
from backend_watermark.config.config import settings

# 创建Celery应用
celery_app = Celery(
    "pureclip",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["backend_watermark.celery_app.tasks"]
)

# 配置Celery
celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_RESULT_SERIALIZER,
    accept_content=settings.CELERY_ACCEPT_CONTENT,
    timezone=settings.CELERY_TIMEZONE,
    enable_utc=settings.CELERY_ENABLE_UTC,
    task_track_started=True,
    task_time_limit=settings.TIMEOUT_PROCESS,
    task_soft_time_limit=settings.TIMEOUT_PROCESS - 30,
)


