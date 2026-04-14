#!/usr/bin/env python
# 检查你的 box.msh 网格是否正常
import meshio

# 读取你的网格文件
mesh = meshio.read("box.msh")

print("="*50)
print("网格信息")
print("="*50)
print(f"总节点数: {len(mesh.points)}")
print(f"节点坐标范围:")
print(f"x: {mesh.points[:,0].min():.4f} ~ {mesh.points[:,0].max():.4f}")
print(f"y: {mesh.points[:,1].min():.4f} ~ {mesh.points[:,1].max():.4f}")
print(f"z: {mesh.points[:,2].min():.4f} ~ {mesh.points[:,2].max():.4f}")
print(f"四面体单元数: {len(mesh.cells_dict['tetra'])}")
print("="*50)

# 打印前5个单元，看看是否正常
print("前 5 个单元信息：")
for i in range(5):
    elem = mesh.cells_dict["tetra"][i]
    pts = mesh.points[elem]
    print(f"单元 {i} 节点ID: {elem}")
    print(f"单元坐标:\n{pts}")
    print("-"*30)
