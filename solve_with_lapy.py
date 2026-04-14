import lapy
import numpy as np
import meshio

# 1. 读取你的网格文件
msh = meshio.read("box.msh")
points = msh.points
cells = msh.cells_dict["tetra"]

# 2. 创建 LaPy 可用的四面体网格对象
tets = lapy.TetMesh(points, cells)

# 3. 创建求解器并组装矩阵
solver = lapy.Solver(tets)

# 4. 定义边界条件（Dirichlet，即电势已知的节点）
# 思路：找到 z=0 (底面) 和 z=1 (顶面) 的节点，并分别设置电势为 0 和 1
z = points[:, 2]
bc_nodes = np.zeros_like(z, dtype=bool)
bc_vals = np.zeros_like(z)

# 标记底面 (z=0) 和顶面 (z=1) 的节点
# 注意：使用容差以避免因浮点误差而错过边界节点
tol = 1e-8
bc_nodes[np.abs(z) < tol] = True
bc_nodes[np.abs(z - 1.0) < tol] = True
# 为这些边界节点赋值：顶面为 1，底面默认为 0
bc_vals[np.abs(z - 1.0) < tol] = 1.0

# 5. 求解泊松方程
# LaPy 的 poisson 方法可以传入 Dirichlet 边界条件
# 其中，bdry_nodes 是需要固定电势的节点，bdry_vals 是这些节点的电势值
u = solver.poisson(bdry_nodes=bc_nodes, bdry_vals=bc_vals)

# 6. 查看结果（可选：与解析解对比）
# 找出中心线附近的节点（例如 x≈0.5, y≈0.5）
center_nodes = (np.abs(points[:, 0] - 0.5) < 0.05) & (np.abs(points[:, 1] - 0.5) < 0.05)
print("z-coordinate, LaPy Solution")
for zi, ui in sorted(zip(points[center_nodes, 2], u[center_nodes])):
    print(f"{zi:.3f}, {ui:.6f}")