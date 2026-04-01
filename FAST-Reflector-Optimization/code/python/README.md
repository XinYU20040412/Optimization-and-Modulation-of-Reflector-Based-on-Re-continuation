# Python Implementation

## 运行方式

在项目根目录执行：

pip install -r code/python/requirements.txt
python code/python/run_showcase.py

## 关键模块

- src/pipeline.py: 总流程控制
- src/q2_pipeline.py: 问题二（遗传算法 + 坐标修正）
- src/ray_models.py: 问题三（接收比计算）
- src/visualization.py: 静态图与 GIF 生成

## 参数配置

配置文件：code/python/config/pipeline_config.json

支持统一配置：

- 几何参数
- 采样参数
- GA 参数
- 动画帧数
- 输入数据路径
