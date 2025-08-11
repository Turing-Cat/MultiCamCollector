# MultiCamCollector 使用说明

MultiCamCollector 是一个专业的多摄像头数据采集应用程序，支持从 Intel RealSense 和 ZED 相机同步采集 RGB-D 数据。

## 目录

- [系统要求](#系统要求)
- [安装指南](#安装指南)
- [配置说明](#配置说明)
- [运行程序](#运行程序)
- [使用指南](#使用指南)
- [数据存储结构](#数据存储结构)
- [故障排除](#故障排除)

## 系统要求

- **操作系统**: Windows 10/11, Linux (推荐 Ubuntu 20.04 或更高版本)
- **Python**: 3.9 或更高版本
- **摄像头 SDK**:
  - Intel RealSense SDK 2.0
  - ZED SDK 4.2.5 或更高版本
- **其他依赖**: 请参见 `requirements.txt` 文件

## 安装指南

### 1. 克隆项目

```bash
git clone <repository-url>
cd MultiCamCollector
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 安装摄像头 SDK

- **Intel RealSense SDK**: 从 [Intel RealSense SDK](https://github.com/IntelRealSense/librealsense) 下载并安装
- **ZED SDK**: 从 [Stereolabs ZED SDK](https://www.stereolabs.com/developers/release/) 下载并安装

## 配置说明

应用程序使用 `config.yaml` 文件进行配置。如果该文件不存在，请复制 `config.yaml.example` 并重命名为 `config.yaml`，然后根据需要修改设置。

### 主要配置项

```yaml
# 相机硬件设置
camera_settings:
  resolution: "1280x720"  # 支持的分辨率: "640x480", "1280x720", "1920x1080"
  fps: 30                 # 帧率: 15, 30, 60

# 后处理设置
post_processing:
  enabled: true          # 启用或禁用整个后处理管道

# UI 性能设置
ui:
  display_fps: 15        # 限制 UI 更新以提高响应速度
  frame_timeout_ms: 500  # 帧捕获超时时间（Linux 优化）
```

## 运行程序

在项目根目录下执行以下命令启动应用程序：

```bash
python src/main.py
```

程序启动后，您将看到一个包含以下组件的图形界面：

1. **相机预览面板**: 显示所有连接相机的实时画面
2. **日志面板**: 显示应用程序运行日志
3. **设置面板**: 配置数据采集选项
4. **控制按钮**: 用于控制采集流程

## 使用指南

### 1. 连接相机

启动程序后，系统会自动检测并连接所有可用的 Intel RealSense 和 ZED 相机。如果未检测到真实相机，程序将使用模拟相机。

### 2. 配置采集设置

在右侧的设置面板中，您可以配置：

- **光照等级**: 选择当前环境的光照条件
- **背景 ID**: 输入当前背景的标识符
- **保存选项**: 选择要保存的数据类型（RGB 图像、深度图像、点云）

### 3. 开始采集

1. 确认所有设置无误
2. 点击 "Capture" 按钮或按空格键开始采集
3. 采集的数据将自动保存到指定目录

### 4. 查看日志

在底部的日志面板中，您可以实时查看应用程序的状态信息、警告和错误。

## 数据存储结构

采集的数据将按照以下结构组织在 `the-dataset` 目录中：

```
the-dataset/
├── YYYYMMDD/              # 日期 (年月日)
│   ├── lighting_level/    # 光照等级
│   │   ├── background_id/ # 背景 ID
│   │   │   ├── seq_001/   # 序列号
│   │   │   │   ├── metadata.json
│   │   │   │   ├── YYYYMMDDTHHMMSSmmm_CameraType_SerialNumber_RGB.png
│   │   │   │   ├── YYYYMMDDTHHMMSSmmm_CameraType_SerialNumber_Depth.tiff
│   │   │   │   └── ...
```

## 故障排除

### 常见问题

1. **未检测到相机**:
   - 确认相机驱动已正确安装
   - 检查 USB 连接
   - 在 Linux 上，可能需要使用管理员权限运行程序

2. **权限错误**:
   - 确保对数据集目录有写入权限
   - 检查相机访问权限

3. **性能问题**:
   - 降低相机分辨率或帧率
   - 关闭其他使用相机的应用程序
   - 检查磁盘空间是否充足

### 查看日志

应用程序会在 `logs/` 目录中创建详细的日志文件。如果遇到问题，请检查最新的日志文件以获取错误详情。