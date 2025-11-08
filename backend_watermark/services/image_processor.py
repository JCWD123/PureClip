"""图片处理服务"""
import cv2
import numpy as np
import os
import uuid
from pathlib import Path
from PIL import Image
from backend_watermark.config.config import settings
from backend_watermark.models.task import WatermarkMethod
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    """图片处理器"""
    
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
        去除图片水印
        
        Args:
            input_file: 输入图片文件路径
            method: 去水印方法
            region: 水印区域坐标 {x, y, width, height}
            
        Returns:
            处理后的图片文件路径
        """
        logger.info(f"开始处理图片: {input_file}, 方法: {method.value}")
        
        # 生成输出文件路径
        output_file = str(self.temp_dir / f"{uuid.uuid4()}.{settings.IMAGE_OUTPUT_FORMAT}")
        
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
            logger.error(f"图片处理失败: {e}")
            raise
    
    def _crop_watermark(
        self,
        input_file: str,
        output_file: str,
        region: Optional[Dict[str, int]]
    ) -> str:
        """
        裁剪方法：去掉图片边角的水印区域
        
        Args:
            input_file: 输入图片
            output_file: 输出图片
            region: 水印区域
            
        Returns:
            输出文件路径
        """
        logger.info("使用裁剪方法去除水印")
        
        img = cv2.imread(input_file)
        height, width = img.shape[:2]
        
        if region:
            x, y, w, h = region['x'], region['y'], region['width'], region['height']
            # 裁剪掉水印区域
            if x == 0 and y == 0:
                # 左上角水印，裁剪掉左上部分
                img = img[h:, w:]
            elif x + w == width and y == 0:
                # 右上角水印
                img = img[h:, :x]
            elif x == 0 and y + h == height:
                # 左下角水印
                img = img[:y, w:]
            elif x + w == width and y + h == height:
                # 右下角水印
                img = img[:y, :x]
            else:
                # 中间水印，裁剪最小包含框
                img = img[0:y if y > 0 else height, 0:x if x > 0 else width]
        else:
            # 默认裁剪底部10%
            new_height = int(height * 0.9)
            img = img[:new_height, :]
        
        cv2.imwrite(output_file, img, [cv2.IMWRITE_JPEG_QUALITY, settings.IMAGE_QUALITY])
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
            input_file: 输入图片
            output_file: 输出图片
            region: 水印区域
            
        Returns:
            输出文件路径
        """
        logger.info("使用模糊方法去除水印")
        
        if not region:
            raise ValueError("模糊方法需要指定水印区域")
        
        img = cv2.imread(input_file)
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        kernel_size = settings.WATERMARK_METHODS['blur']['kernel_size']
        
        # 对水印区域应用高斯模糊
        roi = img[y:y+h, x:x+w]
        blurred = cv2.GaussianBlur(roi, (kernel_size, kernel_size), 0)
        img[y:y+h, x:x+w] = blurred
        
        cv2.imwrite(output_file, img, [cv2.IMWRITE_JPEG_QUALITY, settings.IMAGE_QUALITY])
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
            input_file: 输入图片
            output_file: 输出图片
            region: 水印区域
            
        Returns:
            输出文件路径
        """
        logger.info("使用覆盖方法去除水印")
        
        if not region:
            raise ValueError("覆盖方法需要指定水印区域")
        
        img = cv2.imread(input_file)
        height, width = img.shape[:2]
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        
        # 获取水印区域周围像素的平均颜色
        top = max(0, y - 10)
        bottom = min(height, y + h + 10)
        left = max(0, x - 10)
        right = min(width, x + w + 10)
        
        surrounding = img[top:bottom, left:right]
        avg_color = np.mean(surrounding, axis=(0, 1))
        
        # 用平均颜色覆盖水印区域
        img[y:y+h, x:x+w] = avg_color
        
        cv2.imwrite(output_file, img, [cv2.IMWRITE_JPEG_QUALITY, settings.IMAGE_QUALITY])
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
            input_file: 输入图片
            output_file: 输出图片
            region: 水印区域
            
        Returns:
            输出文件路径
        """
        logger.info("使用填充方法去除水印")
        
        if not region:
            raise ValueError("填充方法需要指定水印区域")
        
        img = cv2.imread(input_file)
        height, width = img.shape[:2]
        x, y, w, h = region['x'], region['y'], region['width'], region['height']
        
        # 创建mask
        mask = np.zeros((height, width), dtype=np.uint8)
        mask[y:y+h, x:x+w] = 255
        
        # 获取inpaint参数
        radius = settings.WATERMARK_METHODS['inpaint']['inpaint_radius']
        
        # 使用OpenCV的inpainting
        inpainted = cv2.inpaint(img, mask, radius, cv2.INPAINT_TELEA)
        
        cv2.imwrite(output_file, inpainted, [cv2.IMWRITE_JPEG_QUALITY, settings.IMAGE_QUALITY])
        logger.info(f"填充处理完成: {output_file}")
        return output_file


