# Code Reproduction Guide

## 目录

- matlab/: 原始问题二 MATLAB 代码归档（用于对照与追溯）。
- python/: 全流程 Python 实现（问题二 + 问题三 + 可视化自动生成）。

## 环境要求

- MATLAB R2020b+
- Python 3.8+

## Python 依赖安装

在项目根目录执行：

pip install -r code/python/requirements.txt

## 一步运行

在项目根目录执行：

python code/python/run_showcase.py

## 运行后自动生成

- results/data/: 调整后节点、伸缩量、关键指标 CSV/JSON
- results/images/: 收敛曲线、接收比柱状图、综合仪表板
- results/animations/: 3D 形变 GIF、2D 光路 GIF、过程动画 GIF

## 主入口说明

- code/python/run_showcase.py: 命令行入口
- code/python/src/pipeline.py: 总管线
- code/python/src/q2_pipeline.py: 问题二模块
- code/python/src/ray_models.py: 问题三反射命中率计算
- code/python/src/visualization.py: 图像与动画生成
