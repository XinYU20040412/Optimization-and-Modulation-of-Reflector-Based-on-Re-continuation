# -*- coding: utf-8 -*-
"""
Created on Sat Aug  3 21:57:06 2024

@author: ASUS
"""
#连接散点图以圈层式线段
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D  # 导入用于三维绘图的Axes3D
import numpy as np
# 指定文件路径
file_path = r"C:\Users\ASUS\AppData\Local\Temp\Rar$DIa35172.26120.rartemp\附件1.csv"

# 使用pandas读取CSV文件
df = pd.read_csv(file_path, encoding='gbk')

# 提取数据
x = df.iloc[:, 1]
y = df.iloc[:, 2]
z = df.iloc[:, 3]
x=np.array(x)
y=np.array(y)
z=np.array(z)
l=[]
for i in range(0,len(x)):
    if x[i]**2+y[i]**2<150*150:
        l.append(i)
x1=[]
y1=[]
z1=[]
for i in l:
    x1.append(x[i])
    y1.append(y[i])
    z1.append(z[i])
ll=[]   
x2=[]
y2=[]
z2=[]
for i in range(0,len(x)):
    if i not in l:
        x2.append(x[i])
        y2.append(y[i])
        z2.append(z[i])
        

# 创建三维散点图
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')
scatter = ax.scatter(x1, y1, z1, color='blue', edgecolor='red')


scatter = ax.scatter(x2, y2, z2, color='green', edgecolor='blue')
    
    




# 连接各点
for i in range(len(x)):
    #ax.plot([x[i]], [y[i]], [z[i]], 'ko')  # 绘制每个点的黑色小圆点
    if i > 0:
        ax.plot([x[i-1], x[i]], [y[i-1], y[i]], [z[i-1], z[i]], color='brown',linestyle='-', linewidth=1)
        
# 设置图像属性
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
ax.set_title('3D Scatter Plot with Connections')

# 保存为EPS格式文件到桌面
desktop_path = r"C:\Users\ASUS\Desktop" # 替换为你的桌面路径
eps_file = f'{desktop_path}\\scatter_plot.eps'
plt.savefig(eps_file, format='eps')

# 显示图形
plt.show()

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

# 指定文件路径，请替换为你的实际路径
file_path = r"C:\Users\ASUS\AppData\Local\Temp\Rar$DIa46684.35213.rartemp\附件1.csv"

# 使用pandas读取CSV文件
df = pd.read_csv(file_path, encoding='gbk')

# 提取数据
x = df.iloc[:, 1]
y = df.iloc[:, 2]
z = df.iloc[:, 3]

# 过滤数据点，选择半径小于150的点
l = (x**2 + y**2) < (150**2)
x1 = x[l]
y1 = y[l]
z1 = z[l]

x2 = x[~l]
y2 = y[~l]
z2 = z[~l]

# 创建三维散点图
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

# 绘制散点图
scatter1 = ax.scatter(x1, y1, z1, c=z1, cmap='viridis', s=50, alpha=0.6, label='Radius < 150')
scatter2 = ax.scatter(x2, y2, z2, c=z2, cmap='inferno', s=50, alpha=0.6, label='Radius >= 150')

# 连接各点
for i in range(len(x)):
    if i > 0:
        ax.plot([x[i-1], x[i]], [y[i-1], y[i]], [z[i-1], z[i]], color='brown', linestyle='-', linewidth=1)

# 设置图像属性
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
ax.set_title('3D Scatter Plot with Connections')
ax.legend()

# 调整视角
ax.view_init(elev=20, azim=30)

# 保存为EPS格式文件到桌面
desktop_path = r"C:\Users\ASUS\Desktop"  # 替换为你的桌面路径
eps_file = f'{desktop_path}\\scatter_plot.eps'
plt.savefig(eps_file, format='eps')


# 显示图形
plt.show()
