# -*- coding: utf-8 -*-
"""
Created on Thu Jul 25 08:24:14 2024

@author: ASUS
"""

#引入最终工作抛物面拟合方程式
def f(x):
    return (1.29916*10**(-6))*x**(3)+0.001551445*x**2+0.005647238*x# 三次拟合工作抛物线方程
import numpy as np
import math
h0=0.466*300.4+0.3786#探测镜距离顶点距离·焦距的四分之一        参数要改
x=np.arange(0,150,0.0001)#设置初始处理点，只考虑一半工作抛物面
y=f(x)#每个初始点的y值
n=len(x)
dy_dx=np.gradient(y, x)#每个点处的导数也就是tanα
Li=[]
Lx=[]
N=0
for i in range(n):
    tan1=dy_dx[i]#tan(alpha)
    tan=(1-tan1**2)/(2*tan1)#tan(90-2alpha)
    delta_h=h0-y[i]
    delta_x=delta_h/tan
    Y=delta_x-x[i]
    idex=i
    nember=x[i]
    if -0.5<=Y<=0.5:
        Li.append(idex)#储存符合解的索引
        Lx.append(nember)   
        N+=1#能射到接收点的数目
bili=N/n
print('工作抛物面有效区域接收到的反射信号与 300 米口径内反射面的反射信号之比为:',bili)
def circl(x):
    return 300-math.sqrt(90000-x**2)

x2=np.arange(0,250,0.0001)#设置初始处理点，只考虑一半基准圆面
n2=len(x2)
y2=[]
for i in range(n2):
    yi=circl(x2[i])
    y2.append(yi)
    
dy_dx2=np.gradient(y2, x2)#每个点处的导数也就是tanα
Li2=[]
Lx2=[]
N2=0
for i in range(n2):
    tan1=dy_dx2[i]#tan(alpha)
    tan=(1-tan1**2)/(2*tan1)#tan(90-2alpha)
    delta_h=h0-y2[i]
    delta_x=delta_h/tan
    Y=delta_x-x2[i]
    idex=i
    nember=x2[i]
    if -0.5<=Y<=0.5:
        Li2.append(idex)#储存符合解的索引
        Lx2.append(nember)   
        N2+=1#能射到接收点的数目
bili=N2/n2
print('基准球面有效区域接收到的反射信号与 500 米口径内反射面的反射信号之比为:',bili)

    
    
    
    









