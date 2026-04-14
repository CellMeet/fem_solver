#!/usr/bin/env python
"""
使用 scikit-fem 验证 Patch Test（直接读取 Gmsh 网格）
"""
import os
import sys
import numpy as np
import meshio
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

# 添加项目路径，以便调用您的网格生成器
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from fem_solver.meshing.gmsh_mesher import GmshMesher

# ------------------------------
# 1. 确保网格文件存在
# ------------------------------
msh_file = "box.msh"
if not os.path.exists(msh_file):
    print(f"未找到 {msh_file}，正在生成网格 (mesh_size=0.3)...")
    GmshMesher.create_box_mesh(0, 1, 0, 1, 0, 1, mesh_size=0.3, filename=msh_file)

# ------------------------------
# 2. 使用 meshio 读取网格
# ------------------------------
print(f"读取网格文件: {msh_file}")
meshio_mesh = meshio.read(msh_file)
points = meshio_mesh.points

# 提取四面体单元
tetra_cells = None
for cell in meshio_mesh.cells:
    if cell.type == "tetra":
        tetra_cells = cell.data
        break
if tetra_cells is None:
    raise ValueError("未找到四面体单元！")

# ------------------------------
# 3. 手动组装刚度矩阵（线性四面体，系数矩阵求逆法）
# ------------------------------
n_nodes = points.shape[0]
n_elements = tetra_cells.shape[0]
print(f"节点数: {n_nodes}, 单元数: {n_elements}")

# 使用 LIL 格式增量组装
A = csr_matrix((n_nodes, n_nodes)).tolil()
b = np.zeros(n_nodes)

bad_count = 0
for elem_idx, cell in enumerate(tetra_cells):
    # 节点坐标 (4x3)
    coords = points[cell]
    # 构建系数矩阵 M = [[1, x0, y0, z0], ...]
    M = np.hstack((np.ones((4, 1)), coords))
    try:
        invM = np.linalg.inv(M)
    except np.linalg.LinAlgError:
        bad_count += 1
        continue
    V = abs(np.linalg.det(M)) / 6.0
    if V < 1e-14:
        bad_count += 1
        continue
    # 梯度矩阵 (4,3)
    grad = invM[1:4, :].T
    # 单元刚度矩阵 (4x4)
    Ke = V * (grad @ grad.T)   # 材料系数 c=1
    # 组装到全局矩阵
    for i_local, i_global in enumerate(cell):
        for j_local, j_global in enumerate(cell):
            A[i_global, j_global] += Ke[i_local, j_local]

A = A.tocsr()
print(f"跳过坏单元数: {bad_count}")

# ------------------------------
# 4. 施加边界条件并求解
# ------------------------------
# 底面 z=0 固定为 0，顶面 z=1 固定为 1
z = points[:, 2]
tol = 1e-12
dofs_bottom = np.where(np.abs(z) < tol)[0]
dofs_top = np.where(np.abs(z - 1.0) < tol)[0]
fixed_dofs = np.union1d(dofs_bottom, dofs_top)
free_dofs = np.setdiff1d(np.arange(n_nodes), fixed_dofs)

print(f"边界自由度: 底面 {len(dofs_bottom)} 个, 顶面 {len(dofs_top)} 个")
print(f"自由度数: {len(free_dofs)}")

# 构建右端项修正（此处 b=0，所以只需处理边界贡献）
u = np.zeros(n_nodes)
u[dofs_bottom] = 0.0
u[dofs_top] = 1.0

# 提取自由子矩阵和右端项
A_ff = A[free_dofs, :][:, free_dofs]
A_fc = A[free_dofs, :][:, fixed_dofs]
u_fixed = u[fixed_dofs]

rhs = -A_fc @ u_fixed   # 因为 b=0
u_free = spsolve(A_ff, rhs)
u[free_dofs] = u_free

# ------------------------------
# 5. 计算误差
# ------------------------------
exact = z
error = u - exact
L2 = np.sqrt(np.mean(error**2))
max_err = np.max(np.abs(error))

print("\n📊 Patch Test 结果 (scikit-fem 手动实现):")
print(f"   L2 误差: {L2:.3e}")
print(f"   最大误差: {max_err:.3e}")

# 输出前5个内部节点验证
print("\n内部节点抽样 (前5个):")
internal_nodes = np.setdiff1d(np.arange(n_nodes), fixed_dofs)
for idx in internal_nodes[:5]:
    print(f"  节点 {idx:4d}  z={z[idx]:.4f}  φ={u[idx]:.8f}  err={error[idx]:.3e}")