# src 模块说明

`src` 负责全部可执行逻辑，按“数据 -> 计算 -> 评估 -> 可视化 -> 汇总”的流水线设计。

## 文件职责

- `constants.py`
  - 定义几何参数、采样参数、可视化主题参数。
  - 所有脚本统一调用，避免魔法数字散落。

- `data_loader.py`
  - 自动发现 `附件1.csv`。
  - 多编码兼容读取（`utf-8-sig` / `gbk` / `gb18030`）。
  - 缺失数据时提供可复现的合成节点云，保证流程可演示。

- `ray_models.py`
  - 工作抛物面与基准球面的轮廓模型。
  - 反射落点计算。
  - 提供循环版与向量化版实现，便于性能对照。

- `benchmark.py`
  - 统一基准测试入口。
  - 输出循环版与向量化版耗时以及加速倍数。

- `visualization.py`
  - 生成仪表板静态图。
  - 生成 GitHub 封面 GIF。
  - 生成参数扫描过程 GIF。

- `pipeline.py`
  - 命令行入口。
  - 编排完整流程并产出 `outputs/summary.json`。

## 二次开发建议

1. 若要替换拟合方程，优先改 `constants.py` 与 `ray_models.py`。
2. 若要接入真实附件，直接将 `附件1.csv` 放入 `data/`。
3. 若要增强视觉风格，集中改 `visualization.py` 中 `PlotStyle`。
