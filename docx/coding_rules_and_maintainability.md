# 二、可读性 & 可维护性规则（Rule）

1. **编码规范**  
   * 遵循 **PEP 8**；强制启用 `ruff` / `black` 自动格式化  
   * 函数、变量采用 *snake_case*，类采用 *PascalCase*

2. **类型与文档**  
   * 100 % **typing** 覆盖；复杂数据结构使用 `TypedDict` / `dataclass`  
   * 所有公共 API 写 **PEP 257** docstring，并在 Cursor/IDE 中启用自动文档生成

3. **分层架构**  
   ```
   gui/         # PYQt 相关
   devices/     # RealSense & ZED 适配器
   services/    # 采集、同步、存储
   models/      # Frame / Metadata dataclass
   utils/       # 通用工具
   ```
   任何业务逻辑不得写在 GUI 层，保持“界面-服务-设备”解耦

4. **日志**  
   * 统一 `loguru`，INFO 以上写文件，DEBUG 只控制台  
   * 日志行包含 *sequence_id*、*camera_id* 等关键信息

5. **错误处理**  
   * 所有 SDK 调用封装为 `try/except`, 自定义 `CameraError`、`CaptureError`  
   * GUI 异常通过 *QtSignal* 上抛到提示框

6. **测试与 CI/CD**  
   * 单元测试覆盖率 ≥ 80 %，PR 若下降则阻断合并  
   * GitHub Actions：`pytest` → `ruff/black` → `pyinstaller --onefile` → 产物上传

7. **配置与魔法数字**  
   * 所有硬编码参数（曝光、帧率、目录规则）写入 `config.yaml`，通过 `pydantic` 校验加载  
   * 禁止在代码中出现硬路径 `D:\Dataset` 等