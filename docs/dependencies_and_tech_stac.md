# Python 依赖清单（建议用 Poetry 或 pip-tools 统一锁版本）

| 功能 | 建议库 | 说明 |
|------|--------|------|
| **RealSense D435i** | `pyrealsense2` | Intel 官方 librealsense Python 绑定 |
| **ZED 2i** | `pyzed-sdk` (or `cython_zed`) | Stereolabs ZED SDK Python 接口 |
| **GUI** | `PySide6` (或 `PyQt6`) | 以 Qt Widgets/QML 还原 HTML 设计中的「多相机网格 + 右侧控制栏」布局 |
| **图像 / 深度处理** | `opencv-python`, `numpy`, `numba` | 预览缩放、深度伪彩等 |
| **异步与多线程** | `asyncio`, `qasync`, `concurrent.futures` | GUI 主线程 + 采集/写盘后台线程 |
| **数据持久化** | `h5py` 或 `zarr`, `tifffile` | 大批量 RGB-D 帧顺序写 |
| **日志** | `loguru` | 彩色终端 + 文件旋转 |
| **配置** | `pydantic` | 校验 `.yaml` / `.json` |
| **测试** | `pytest`, `pytest-qt` | 单元 + GUI 自动化 |
| **打包** | `pyinstaller` 或 `briefcase` | 生成 Windows/MSI、Linux/AppImage |