# 三、问题拆解与开发流程

| # | 子问题 | 目标产物 | 主要步骤 |
|---|--------|---------|---------|
| 1 | **设备抽象层** | `AbstractCamera` 基类 + `D435iCamera` / `Zed2iCamera` | ➊ 设计接口 → ➋ 写伪实现+单测 → ➌ 集成 SDK → ➍ Mock 相机通过单测 |
| 2 | **设备发现 & 状态监控** | `DeviceManager` | ➊ 枚举 USB/PCIe 序列号 → ➋ 心跳线程 → ➌ 状态信号给 GUI |
| 3 | **帧采集与五路同步** | `CaptureOrchestrator` | ➊ 软触发 + 时间戳 → ➋ 校验最大抖动 <1 帧 → ➌ 单测: 模拟 5 路随机延迟 |
| 4 | **实时预览渲染** | `PreviewWidget` | ➊ QThread 拉流 → ➋ 缩放到 GUI 网格 → ➌ FPS 叠字 |
| 5 | **元数据配置 & 锁定** | `MetadataPanel` | ➊ UI 两向绑定模型 → ➋ 锁定后禁用输入 → ➌ 单测验证 JSON 输出 |
| 6 | **数据保存子系统** | `StorageService` | ➊ 目录规则 yyyyMMdd/seq → ➋ HDF5 + PNG 写盘 → ➌ 队列限流 |
| 7 | **序列号与进度计** | `SequenceCounter` | ➊ 原子自增 → ➋ 断电续采时自动恢复 |
| 8 | **系统日志 UI** | `LogPanel` | ➊ 日志级别彩色映射 → ➋ 自动滚动，最多保存 200 行 |
| 9 | **配置 & 启动脚本** | `main.py`, `config.yaml` | ➊ 解析 CLI 参数 → ➋ 读取配置 → ➌ 初始化各组件 |
| 10 | **安装与发布** | `build.spec` | ➊ PyInstaller 打包 → ➋ 自动拷贝 RealSense & ZED DLL/SO |

> **统一流程**（每个子问题都遵循）  
> 1. **需求→设计**：在 issues 中记录接口草图 & 时序图。  
> 2. **接口→测试**：先编写最小可运行单元测试（TDD）。  
> 3. **实现→自测**：本地跑 `pytest -q` & GUI smoke test。  
> 4. **PR→Code Review**：至少一人审查；CI 需全部绿灯。  
> 5. **合并→集成**：拉取最新 `main`，解决冲突，再合并。  
> 6. **迭代→回顾**：Sprint 结束进行 burndown 及问题复盘。
