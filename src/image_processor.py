#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
图像处理模块，用于手机壳图片的识别和合成
"""

import os
import cv2
import numpy as np
from PIL import Image, ImageChops
from typing import Tuple, Optional, Dict, Any
import logging

from utils import setup_logger

logger = setup_logger()


class ImageProcessor:
    """手机壳图像处理器"""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        初始化图像处理器
        
        Args:
            config: 配置参数字典
        """
        self.config = config or {}
        self.default_config = {
            "output_quality": 95,            # 输出图片质量
            "output_format": "png",          # 输出图片格式
            "auto_adjust_brightness": True,  # 自动调整亮度
            "auto_adjust_contrast": True,    # 自动调整对比度
            "detect_edges": True,            # 检测边缘
            "resize_method": "lanczos",      # 调整大小的方法
        }
        
        # 合并默认配置和用户配置
        for key, value in self.default_config.items():
            if key not in self.config:
                self.config[key] = value
    
    def load_image(self, image_path: str) -> Optional[Image.Image]:
        """
        加载图片文件
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            加载后的PIL图像对象，如果加载失败则返回None
        """
        try:
            image = Image.open(image_path)
            # 确保图像有Alpha通道
            if image.mode != 'RGBA':
                image = image.convert('RGBA')
            return image
        except Exception as e:
            logger.error(f"加载图片 {image_path} 失败: {str(e)}")
            return None
    
    def detect_phone_case(self, case_image: Image.Image) -> Image.Image:
        """
        检测手机壳图片并提取
        
        Args:
            case_image: 手机壳图片对象
            
        Returns:
            处理后的手机壳图片
        """
        # 转换为OpenCV格式进行处理
        case_cv = np.array(case_image)
        # BGR to RGBA
        case_cv = cv2.cvtColor(case_cv, cv2.COLOR_RGBA2BGRA)
        
        # 如果配置为检测边缘
        if self.config["detect_edges"]:
            # 提取alpha通道作为掩码
            alpha = case_cv[:, :, 3]
            
            # 使用阈值处理创建二值掩码
            _, mask = cv2.threshold(alpha, 10, 255, cv2.THRESH_BINARY)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 如果找到轮廓
            if contours:
                # 找到最大的轮廓（假设是手机壳）
                max_contour = max(contours, key=cv2.contourArea)
                
                # 创建空白蒙版
                refined_mask = np.zeros_like(mask)
                
                # 在蒙版上绘制最大轮廓
                cv2.drawContours(refined_mask, [max_contour], 0, 255, -1)
                
                # 将原始alpha值应用到精细蒙版上
                refined_alpha = cv2.bitwise_and(alpha, refined_mask)
                
                # 更新图像的alpha通道
                case_cv[:, :, 3] = refined_alpha
        
        # 回到PIL格式
        case_processed = Image.fromarray(cv2.cvtColor(case_cv, cv2.COLOR_BGRA2RGBA))
        
        # 自动调整亮度和对比度
        if self.config["auto_adjust_brightness"] or self.config["auto_adjust_contrast"]:
            from PIL import ImageEnhance
            
            if self.config["auto_adjust_brightness"]:
                enhancer = ImageEnhance.Brightness(case_processed)
                case_processed = enhancer.enhance(1.1)  # 略微提高亮度
            
            if self.config["auto_adjust_contrast"]:
                enhancer = ImageEnhance.Contrast(case_processed)
                case_processed = enhancer.enhance(1.1)  # 略微提高对比度
        
        return case_processed
    
    def find_template_placeholder(self, template_image: Image.Image) -> Tuple[int, int, int, int]:
        """
        在模板中查找手机壳的占位区域
        
        Args:
            template_image: 模板图片对象
            
        Returns:
            占位区域的坐标 (x, y, width, height)
        """
        # 转换为OpenCV格式
        template_cv = np.array(template_image)
        template_cv = cv2.cvtColor(template_cv, cv2.COLOR_RGBA2BGRA)
        
        # 提取alpha通道
        alpha = template_cv[:, :, 3]
        
        # 查找alpha值较低的区域（假设这是手机壳应该放置的位置）
        low_alpha_mask = cv2.threshold(alpha, 100, 255, cv2.THRESH_BINARY_INV)[1]
        
        # 查找轮廓
        contours, _ = cv2.findContours(low_alpha_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 如果找到轮廓
        if contours:
            # 找到面积最大的轮廓（假设是手机壳位置）
            max_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(max_contour)
            return (x, y, w, h)
        
        # 如果没找到，返回模板的中心位置
        width, height = template_image.size
        return (width // 4, height // 4, width // 2, height // 2)
    
    def composite_images(self, case_image: Image.Image, template_image: Image.Image) -> Image.Image:
        """
        将手机壳图像合成到模板中
        
        Args:
            case_image: 处理过的手机壳图像
            template_image: 模板图像
            
        Returns:
            合成后的图像
        """
        # 查找模板中的占位区域
        x, y, w, h = self.find_template_placeholder(template_image)
        
        # 调整手机壳图像大小以适应占位区域
        case_resized = case_image.resize((w, h), getattr(Image, self.config["resize_method"].upper()))
        
        # 创建模板的副本
        result = template_image.copy()
        
        # 将手机壳图像粘贴到模板中
        result.paste(case_resized, (x, y), case_resized)
        
        return result
    
    def process_images(self, case_path: str, template_path: str, output_path: str) -> bool:
        """
        处理单个手机壳图像和模板
        
        Args:
            case_path: 手机壳图像路径
            template_path: 模板图像路径
            output_path: 输出图像路径
            
        Returns:
            处理成功返回True，否则返回False
        """
        try:
            # 加载图像
            case_image = self.load_image(case_path)
            template_image = self.load_image(template_path)
            
            if not case_image or not template_image:
                return False
            
            # 处理手机壳图像
            case_processed = self.detect_phone_case(case_image)
            
            # 合成图像
            result_image = self.composite_images(case_processed, template_image)
            
            # 保存结果
            output_format = self.config["output_format"].upper()
            if output_format == 'JPG':
                output_format = 'JPEG'
            
            result_image.save(
                output_path,
                format=output_format,
                quality=self.config["output_quality"]
            )
            
            logger.info(f"成功生成商品图: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"处理图像失败: {str(e)}")
            return False
