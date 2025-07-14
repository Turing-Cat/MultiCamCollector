# Todo List

- [x] 1.  Add post-processing for RealSense depth data.

推荐的滤波器链及参数设置：
  1. 降采样滤波器 (Decimation Filter): 不启用
    - 以原分辨率采集再离线降采样
    - 理由: 抓取算法依赖高频细节（细爪或细纹理），保留原分辨率
  2. 深度到视差转换 (Depth to Disparity Transform): 启用
    - 理由: 这是至关重要的一步。对于D400系列立体相机，在更线性的视差域中进行空间和时间滤波，可以获得比直接在深度域中操作更高质量、更少伪影的结果 7。
  3. 空间滤波器 (Spatial Filter): 启用
    - Smooth Alpha: 0.5
    - Smooth Delta: 25 (此为关键调优参数)
    - Magnitude: 2
    - Hole Filling: 0 (禁用)
    - 理由: 这是保证抓取数据质量的核心滤波器。它的保边功能能够有效平滑物体表面噪声，同时保护抓取规划所依赖的物体轮廓 13。
Smooth Delta值需要根据被抓取物体的特征进行微调：对于特征精细的物体，可适当调低此值；对于表面平滑的物体，可适当调高。此处的孔洞填充功能较为简单，建议禁用，交由后续专用滤波器处理。
  4. 时间滤波器 (Temporal Filter): 谨慎启用
    - Smooth Alpha: 0.1 (保守设置)
    - Smooth Delta: 20 (较高设置)
    - Persistency Index: 0 (禁用)
    - 理由: 对于采集静态物体的数据集，启用时间滤波可以有效减少帧间抖动。但必须坚决禁用持久性填充（Persistency Index > 0），因为它会引入严重的运动伪影，一旦相机或物体有轻微移动，就会产生错误的几何形状，从而“毒化”数据集 20。
  5. 视差到深度转换 (Disparity to Depth Transform): 启用
    - 理由: 将经过优化的视差数据转换回应用程序可以直接使用的深度数据。
  6. 孔洞填充滤波器 (Holes Filling Filter): 考虑启用
    - Fill Method: nearest_from_around
    - 理由: 在所有滤波步骤之后，如果仍存在少量小空洞，可以使用此滤波器进行最后的修补。选择nearest_from_around策略通常比其他策略更安全，因为它倾向于用离相机较近的（很可能是前景物体）像素值来填充空洞，而不是用离相机较远的（很可能是背景）像素值 6。