# Results Interpretation

## 文件夹说明

- data/: 数值结果与中间数据
- images/: 静态图
- animations/: 动态 GIF

## 静态图解读

1. images/q2_ga_convergence.png
含义：问题二遗传算法收敛曲线。
曲线：平均 RMSE 与最优 RMSE 双折线，展示优化稳定性。

2. images/acceptance_comparison.png
含义：工作抛物面与基准球面的接收比柱状对比图。
要点：工作面显著高于基准面。

3. images/dashboard.png
含义：轮廓、落点分布、性能加速、节点云来源的综合看板。

## 动图解读

1. animations/surface_morph.gif
含义：FAST 基准球面到工作抛物面的 3D 形变过程。
特征：镜面网格 + 由远及近视角，突出 300m 有效口径区域调控。

2. animations/ray_path_2d.gif
含义：降维平面化后的电磁波入射-反射-汇聚过程。
高亮：绿色为有效光线，红色为无效光线。

3. animations/optimization_process.gif
含义：工作面与基准面接收率随扫描进度的动态对比。

4. animations/h0_parameter_sweep.gif
含义：接收舱参数 h0 变化对接收比的影响。

## 数据字段说明

1. data/q2_adjusted_nodes.csv
- node: 节点编号
- x, y, z: 调整后全局坐标（单位 m）

2. data/q2_flex_lengths.csv
- node: 节点编号
- theta_rad: 节点极角（弧度）
- flex_length_m: 促动器伸缩量（单位 m）

3. data/key_metrics.csv
- metric: 指标名称
- value: 指标值

4. summary.json
- geometry/sampling/q2: 参数记录
- acceptance_ratio: 接收比与提升
- benchmark: 向量化性能对比
- artifacts: 所有图像与数据文件索引
