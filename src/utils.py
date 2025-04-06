#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
工具函数模块，提供辅助功能
"""

import os
import logging
import glob
from typing import List, Union, Tuple
import time


def setup_logger(log_level: int = logging.INFO) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        log_level: 日志级别，默认为INFO
        
    Returns:
        配置好的logger对象
    """
    logger = logging.getLogger("phonecase")
    logger.setLevel(log_level)
    
    # 如果已经有处理器，则不再添加
    if logger.handlers:
        return logger
        
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 设置日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器到logger
    logger.addHandler(console_handler)
    
    return logger


def get_file_paths(input_path: str, extensions: List[str] = None) -> List[str]:
    """
    获取指定路径下的所有文件路径
    
    Args:
        input_path: 输入路径（文件或目录）
        extensions: 文件扩展名列表，如 ['.jpg', '.png']
        
    Returns:
        文件路径列表
    """
    if extensions is None:
        extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
    # 标准化扩展名
    extensions = [ext.lower() if not ext.startswith('.') else ext.lower() for ext in extensions]
    
    # 如果输入是文件
    if os.path.isfile(input_path):
        ext = os.path.splitext(input_path)[1].lower()
        if not extensions or ext in extensions:
            return [input_path]
        return []
    
    # 如果输入是目录
    if os.path.isdir(input_path):
        file_paths = []
        for ext in extensions:
            pattern = os.path.join(input_path, f"*{ext}")
            file_paths.extend(glob.glob(pattern))
        return sorted(file_paths)
    
    return []


def ensure_directory(directory: str) -> str:
    """
    确保目录存在，如果不存在则创建
    
    Args:
        directory: 目录路径
        
    Returns:
        创建后的目录路径
    """
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
    return directory


def generate_output_filename(
    input_path: str,
    template_path: str,
    output_dir: str,
    name_pattern: str = "{input}_{template}",
    output_format: str = "png"
) -> str:
    """
    生成输出文件名
    
    Args:
        input_path: 输入文件路径
        template_path: 模板文件路径
        output_dir: 输出目录
        name_pattern: 文件名模式
        output_format: 输出格式
        
    Returns:
        完整的输出文件路径
    """
    # 获取文件名（不含扩展名）
    input_name = os.path.splitext(os.path.basename(input_path))[0]
    template_name = os.path.splitext(os.path.basename(template_path))[0]
    
    # 替换模式中的变量
    filename = name_pattern.format(
        input=input_name,
        template=template_name,
        timestamp=int(time.time())
    )
    
    # 添加扩展名
    if not output_format.startswith('.'):
        output_format = f".{output_format}"
    
    # 组合完整路径
    return os.path.join(output_dir, f"{filename}{output_format}")


def is_valid_image(file_path: str) -> bool:
    """
    检查文件是否为有效的图像文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        如果是有效的图像文件，返回True，否则返回False
    """
    valid_extensions = ['.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tiff']
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext not in valid_extensions:
        return False
    
    if not os.path.isfile(file_path) or os.path.getsize(file_path) == 0:
        return False
    
    return True
