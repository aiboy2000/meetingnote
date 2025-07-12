# Windows安装指南

## 系统要求
- Windows 10/11
- Python 3.8-3.11（推荐3.10）
- 16GB RAM推荐

## 安装步骤

### 1. Python环境准备
```powershell
# 检查Python版本
python --version

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate
```

### 2. 安装核心依赖

```powershell
# 升级pip
python -m pip install --upgrade pip

# 安装PyTorch（CPU版本）
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cpu

# 安装其他依赖
pip install -r requirements-windows.txt
```

### 3. 解决常见问题

#### FFmpeg安装
```powershell
# 下载FFmpeg: https://ffmpeg.org/download.html
# 或使用chocolatey
choco install ffmpeg
```

#### MeCab安装（可选，用于日语处理）
```powershell
# 下载MeCab for Windows
# https://github.com/ikegami-yukino/mecab/releases
```

#### pyaudio问题（如果需要实时音频）
```powershell
# 如果安装失败，下载对应版本的wheel文件
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
pip install pyaudio-0.2.11-cp310-cp310-win_amd64.whl
```

### 4. 验证安装

```powershell
# 语法检查
python syntax_test.py

# 基本功能测试（部分功能）
python -c "import torch; import transformers; import gradio; print('安装成功！')"
```

### 5. 启动应用

```powershell
python main.py
```

然后在浏览器访问：http://localhost:7860

## 简化版安装（最小依赖）

如果遇到安装问题，可以先安装核心功能：

```powershell
pip install gradio transformers sentence-transformers pdfplumber requests
```

这将提供基本的PDF处理和Web界面功能。

## GPU加速（可选）

如果有NVIDIA GPU：

```powershell
# 安装CUDA版本的PyTorch
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## 故障排除

### 常见错误解决

1. **Microsoft Visual C++ 错误**
   - 安装 Visual Studio Build Tools
   - 或下载 Microsoft Visual C++ Redistributable

2. **权限错误**
   - 以管理员身份运行PowerShell
   - 或使用 `--user` 标志：`pip install --user package`

3. **网络问题**
   - 使用国内镜像：`pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/`

4. **内存不足**
   - 关闭其他应用程序
   - 使用较小的模型（Whisper base instead of large）