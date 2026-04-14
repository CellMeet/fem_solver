import meshio
import numpy as np

mesh = meshio.read("electrostatic_result.vtk")
points = mesh.points
phi = mesh.point_data["solution"]

print("节点数:", len(points))
print("单元类型:", [c.type for c in mesh.cells])

# 底面和顶面节点电势
z = points[:, 2]
bottom = np.isclose(z, 0, atol=1e-5)
top = np.isclose(z, 1, atol=1e-5)
print(f"底面节点数: {np.sum(bottom)}，电势范围: {phi[bottom].min():.6f} ~ {phi[bottom].max():.6f}")
print(f"顶面节点数: {np.sum(top)}，电势范围: {phi[top].min():.6f} ~ {phi[top].max():.6f}")

# 内部节点电势
inside = ~(bottom | top)
print(f"内部节点数: {np.sum(inside)}，电势范围: {phi[inside].min():.6f} ~ {phi[inside].max():.6f}")

# 检查是否有四面体单元
if any(c.type == "tetra" for c in mesh.cells):
    print("✓ 包含四面体单元")
else:
    print("✗ 缺少四面体单元，只有表面网格")
