#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
手机壳商品图自动生成系统主程序
"""

import os
import sys
import argparse
import logging
from tqdm import tqdm
import time

from utils import setup_logger, get_file_paths, ensure_directory, generate_output_filename
from image_processor import ImageProcessor

# 设置日志
logger = setup_logger()


def parse_arguments():
    """
    解析命令行参数
    
    Returns:
        解析后的参数
    """
    parser = argparse.ArgumentParser(description='手机壳商品图自动生成系统')
    
    parser.add_argument('--input', '-i', required=True, 
                        help='输入的手机壳图片路径或目录')
    
    parser.add_argument('--template', '-t', required=True,
                        help='模板图片路径或目录')
    
    parser.add_argument('--output', '-o', required=True,
                        help='输出图片保存目录')
    
    parser.add_argument('--quality', '-q', type=int, default=95,
                        help='输出图片质量(1-100)，默认为95')
    
    parser.add_argument('--format', '-f', default='png',
                        choices=['png', 'jpg', 'jpeg', 'webp'],
                        help='输出图片格式，默认为png')
    
    parser.add_argument('--name-pattern', '-n', default='{input}_{template}',
                        help='输出文件命名模式，默认为{input}_{template}')
    
    parser.add_argument('--brightness', type=float, default=1.1,
                        help='亮度调整系数，默认为1.1')
    
    parser.add_argument('--contrast', type=float, default=1.1,
                        help='对比度调整系数，默认为1.1')
    
    parser.add_argument('--no-edge-detection', action='store_true',
                        help='禁用边缘检测')
    
    parser.add_argument('--resize-method', default='lanczos',
                        choices=['nearest', 'box', 'bilinear', 'hamming', 'bicubic', 'lanczos'],
                        help='图像缩放方法，默认为lanczos')
    
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='输出详细日志')
    
    args = parser.parse_args()
    
    # 验证参数
    if args.quality < 1 or args.quality > 100:
        parser.error("质量参数必须在1-100之间")
    
    return args


def process_batch(processor, case_paths, template_paths, output_dir, name_pattern, output_format):
    """
    批量处理图片
    
    Args:
        processor: 图像处理器
        case_paths: 手机壳图片路径列表
        template_paths: 模板图片路径列表
        output_dir: 输出目录
        name_pattern: 文件命名模式
        output_format: 输出格式
        
    Returns:
        成功处理的数量
    """
    total_tasks = len(case_paths) * len(template_paths)
    success_count = 0
    
    # 使用tqdm创建进度条
    progress_bar = tqdm(total=total_tasks, desc="处理图片")
    
    for case_path in case_paths:
        for template_path in template_paths:
            # 生成输出文件路径
            output_path = generate_output_filename(
                case_path, template_path, output_dir, name_pattern, output_format
            )
            
            # 处理图片
            if processor.process_images(case_path, template_path, output_path):
                success_count += 1
            
            # 更新进度条
            progress_bar.update(1)
    
    progress_bar.close()
    return success_count


def main():
    """主函数"""
    # 解析命令行参数
    args = parse_arguments()
    
    # 设置日志级别
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 获取手机壳图片路径列表
    case_paths = get_file_paths(args.input)
    if not case_paths:
        logger.error(f"没有找到有效的图片文件: {args.input}")
        return 1
    
    # 获取模板图片路径列表
    template_paths = get_file_paths(args.template)
    if not template_paths:
        logger.error(f"没有找到有效的模板文件: {args.template}")
        return 1
    
    # 确保输出目录存在
    output_dir = ensure_directory(args.output)
    
    # 创建图像处理器配置
    config = {
        "output_quality": args.quality,
        "output_format": args.format,
        "auto_adjust_brightness": True,
        "auto_adjust_contrast": True,
        "detect_edges": not args.no_edge_detection,
        "resize_method": args.resize_method,
        "brightness_factor": args.brightness,
        "contrast_factor": args.contrast
    }
    
    # 创建图像处理器
    processor = ImageProcessor(config)
    
    logger.info(f"开始处理 {len(case_paths)} 个手机壳图片 和 {len(template_paths)} 个模板")
    
    # 记录开始时间
    start_time = time.time()
    
    # 批量处理图片
    success_count = process_batch(
        processor, case_paths, template_paths,
        output_dir, args.name_pattern, args.format
    )
    
    # 计算耗时
    elapsed_time = time.time() - start_time
    
    # 输出结果
    logger.info(f"处理完成！成功: {success_count}/{len(case_paths) * len(template_paths)}")
    logger.info(f"总耗时: {elapsed_time:.2f} 秒")
    logger.info(f"生成的图片保存在: {os.path.abspath(output_dir)}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
