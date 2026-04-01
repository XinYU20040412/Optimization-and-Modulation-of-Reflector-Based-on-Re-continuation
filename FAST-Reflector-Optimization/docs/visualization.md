# Visualization Design Notes

## 视觉目标

1. 访问者不运行代码，也能在首页快速理解项目价值。
2. 通过动图讲清几何变形和光路命中机制。
3. 通过静态图给出可复查的关键指标。

## 产物清单

1. results/animations/surface_morph.gif
- 内容：基准球面到工作抛物面的连续形变。
- 风格：蓝白科技色 + 网格结构 + 由远及近视角。

2. results/animations/ray_path_2d.gif
- 内容：降维平面内入射-反射-接收过程。
- 颜色语义：绿色有效，红色无效。

3. results/images/q2_ga_convergence.png
- 内容：问题二遗传算法收敛曲线。

4. results/images/acceptance_comparison.png
- 内容：工作抛物面 vs 基准球面接收比柱状图。

5. results/images/dashboard.png
- 内容：算法结果、性能对比、节点云来源总览。

## 设计原则

1. 颜色对比明确：工作面主色与基准面对比色固定。
2. 指标直出：重要数值写入图中避免二次解释。
3. 路径统一：全部产物输出到 results，便于 README 直接引用。
