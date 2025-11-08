"""视频处理服务"""
import subprocess
import cv2
import numpy as np
import os
import uuid
from pathlib import Path
from backend_watermark.config.config import settings
from backend_watermark.models.task import WatermarkMethod
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class VideoProcessor:
    """视频处理器"""
    
    def __init__(self):
        self.temp_dir = Path(settings.VIDEO_TEMP_DIR)
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def remove_watermark(
        self,
        input_file: str,
        method: WatermarkMethod,
        region: Optional[Dict[str, int]] = None
    ) -> str:
        """
        去除视频水印
        
        Args:
            input_file: 输入视频文件路径
            method: 去水印方法
            region: 水印区域坐标 {x, y, width, height}
            
        Returns:
            处理后的视频文件路径
        """
        logger.info(f"开始处理视频: {input_file}, 方法: {method.value}")
        
        # 生成输出文件路径
        output_file = str(self.temp_dir / f"{uuid.uuid4()}.{settings.VIDEO_OUTPUT_FORMAT}")
        
        try:
            if method == WatermarkMethod.CROP:
                return self._crop_watermark(input_file, output_file, region)
            elif method == WatermarkMethod.BLUR:
                return self._blur_watermark(input_file, output_file, region)
            elif method == WatermarkMethod.COVER:
                return self._cover_watermark(input_file, output_file, region)
            elif method == WatermarkMethod.INPAINT:
                return self._inpaint_watermark(input_file, output_file, region)
            else:
                raise ValueError(f"不支持的方法: {method}")
                
        except Exception as e:
            logger.error(f"视频处理失败: {e}")
            raise
    
    def _crop_watermark(
        self,
        input_file: str,
        output_file: str,
        region: Optional[Dict[str, int]]
    ) -> str:
        """
        裁剪方法：去掉视频边角的水印区域
        
        Args:
            input_file: 输入视频
            output_file: 输出视频
            region: 水印区域（如果为None，默认裁剪底部10%）
            
        Returns:
            输出文件路径
        """
        logger.info("使用裁剪方法去除水印")
        
        # 获取视频信息
        cap = cv2.VideoCapture(input_file)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        cap.release()
        
        # 计算裁剪区域
        if region:
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            crop_w = width - w
            crop_h = height - h
            crop_x = x if x > 0 else 0
            crop_y = y if y > 0 else 0
        else:
            # 默认裁剪底部10%
            crop_w = width
            crop_h = int(height * 0.9)
            crop_x = 0
            crop_y = 0
        
        # 使用ffmpeg裁剪
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-vf', f'crop={crop_w}:{crop_h}:{crop_x}:{crop_y}',
            '-c:a', 'copy',
            '-y',
            output_file
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"裁剪完成: {output_file}")
        return output_file
    
    def _blur_watermark(
        self,
        input_file: str,
        output_file: str,
        region: Optional[Dict[str, int]]
    ) -> str:
        """
        模糊方法：高斯模糊水印区域
        
        Args:
            input_file: 输入视频
            output_file: 输出视频
            region: 水印区域
            
        Returns:
            输出文件路径
        """
        logger.info("使用模糊方法去除水印")
        
        if not region:
            raise ValueError("模糊方法需要指定水印区域")
        
        # 读取视频
        cap = cv2.VideoCapture(input_file)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
        
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        kernel_size = settings.WATERMARK_METHODS['blur']['kernel_size']
        
        # 处理每一帧
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 对水印区域应用高斯模糊
            roi = frame[y:y+h, x:x+w]
            blurred = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)
            frame[y:y+h, x:x+w] = blurred
            
            out.write(frame)
        
        cap.release()
        out.release()
        
        logger.info(f"模糊处理完成: {output_file}")
        return output_file
    
    def _cover_watermark(
        self,
        input_file: str,
        output_file: str,
        region: Optional[Dict[str, int]]
    ) -> str:
        """
        覆盖方法：用背景颜色或局部像素平均覆盖
        
        Args:
            input_file: 输入视频
            output_file: 输出视频
            region: 水印区域
            
        Returns:
            输出文件路径
        """
        logger.info("使用覆盖方法去除水印")
        
        if not region:
            raise ValueError("覆盖方法需要指定水印区域")
        
        # 读取视频
        cap = cv2.VideoCapture(input_file)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
        
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        
        # 处理每一帧
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 获取水印区域周围像素的平均颜色
            top = max(0, y - 10)
            bottom = min(height, y + h + 10)
            left = max(0, x - 10)
            right = min(width, x + w + 10)
            
            surrounding = frame[top:bottom, left:right]
            avg_color = np.mean(surrounding, axis=(0, 1))
            
            # 用平均颜色覆盖水印区域
            frame[y:y+h, x:x+w] = avg_color
            
            out.write(frame)
        
        cap.release()
        out.release()
        
        logger.info(f"覆盖处理完成: {output_file}")
        return output_file
    
    def _inpaint_watermark(
        self,
        input_file: str,
        output_file: str,
        region: Optional[Dict[str, int]]
    ) -> str:
        """
        填充方法：使用OpenCV的inpainting修补水印
        
        Args:
            input_file: 输入视频
            output_file: 输出视频
            region: 水印区域
            
        Returns:
            输出文件路径
        """
        logger.info("使用填充方法去除水印")
        
        if not region:
            raise ValueError("填充方法需要指定水印区域")
        
        # 读取视频
        cap = cv2.VideoCapture(input_file)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # 创建视频写入器
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_file, fourcc, fps, (width, height))
        
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        
        # 创建mask
        mask = np.zeros((height, width), dtype=np.uint8)
        mask[y:y+h, x:x+w] = 255
        
        # 获取inpaint参数
        radius = settings.WATERMARK_METHODS['inpaint']['inpaint_radius']
        
        # 处理每一帧
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # 使用OpenCV的inpainting
            inpainted = cv2.inpaint(frame, mask, radius, cv2.INPAINT_TELEA)
            out.write(inpainted)
        
        cap.release()
        out.release()
        
        logger.info(f"填充处理完成: {output_file}")
        return output_file


