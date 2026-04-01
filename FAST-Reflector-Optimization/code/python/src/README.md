# src 模块结构

该目录按 数据 -> 算法 -> 可视化 -> 管线 的方式组织。

- constants.py
  统一配置 dataclass（几何参数、采样、GA、动画）

- data_loader.py
  数据发现与读取，支持多编码和无数据回退

- q2_ga.py
  问题二遗传算法核心（初始化、变异、交叉、适应度）

- q2_geometry.py
  问题二坐标变换与节点伸缩计算（含 bug 修复）

- q2_pipeline.py
  问题二流程总控与 CSV/JSON 结果落盘

- ray_models.py
  问题三反射命中率计算（向量化 + 循环对照）

- benchmark.py
  计算性能对比

- visualization.py
  仪表板、柱状图、3D/2D 动画生成

- pipeline.py
  全项目一键入口，串联问题二与问题三
