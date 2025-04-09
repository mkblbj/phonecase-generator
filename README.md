# 手机壳商品图自动生成系统

## 项目介绍
手机壳商品图自动生成系统是一个专为手机壳电商平台设计的自动化图片处理工具。该系统能够根据上传的手机壳实物图片和预设的模板，自动生成符合电商平台规范的商品展示图，大幅提高商品图制作效率，保证图片质量的一致性。

## 功能特点
- **智能合成**：自动识别手机壳边缘，智能填充到模板中
- **批量处理**：支持同时处理多张手机壳图片，提高工作效率
- **多种模板**：内置多种商品展示模板，满足不同展示需求
- **高质量输出**：保持图片的透明度和细节，确保输出质量
- **灵活配置**：支持自定义输出路径、文件名和图片参数

## 安装说明

### 系统要求
- Python 3.8 或更高版本
- 支持 Windows、MacOS 和 Linux 操作系统

### 安装步骤

1. **克隆项目仓库**
```bash
git clone https://github.com/yourusername/PhoneCase.git
cd PhoneCase
```

2. **安装依赖**
```bash
pip install -r src/requirements.txt
```

## 使用方法

### 基本使用

```bash
python src/main.py --input data/samples/case1.png --template data/templates/template1.png --output data/output/
```

### 批量处理

```bash
python src/main.py --input data/samples/ --template data/templates/template1.png --output data/output/
```

### 使用多个模板

```bash
python src/main.py --input data/samples/case1.png --template data/templates/ --output data/output/
```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--input`, `-i` | 输入图片或目录 | 必填 |
| `--template`, `-t` | 模板图片或目录 | 必填 |
| `--output`, `-o` | 输出目录 | 必填 |
| `--quality`, `-q` | 输出图片质量(1-100) | 95 |
| `--format`, `-f` | 输出图片格式 | png |
| `--name-pattern`, `-n` | 输出文件命名模式 | {input}_{template} |

## 目录结构

```
PhoneCase/
├── data/
│   ├── samples/       # 手机壳样品图片
│   ├── templates/     # 模板图片
│   └── output/        # 输出图片
├── docs/
│   └── __requirements__.md     # 项目需求文档
├── src/
│   ├── main.py           # 主程序入口
│   ├── image_processor.py # 图像处理模块
│   ├── utils.py          # 工具函数
│   └── requirements.txt  # 项目依赖
└── README.md             # 项目说明
```

## 技术栈
- **Python**：主要开发语言
- **OpenCV**：图像处理和识别
- **Pillow**：图像合成和输出
- **NumPy**：数据处理
- **tqdm**：进度显示

## 许可证
本项目采用 MIT 许可证。

