#!/usr/bin/env python
"""
直接求解器（参考实现）
使用 scipy.sparse 组装四面体单元，求解拉普拉斯方程
边界条件：底面 z=0 → 0V，顶面 z=1 → 1V
"""

import numpy as np
import meshio
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve

# ------------------------------
# 1. 读取网格
# ------------------------------
print("读取网格 box.msh ...")
mesh = meshio.read("box.msh")
points = mesh.points          # (N, 3)
cells = mesh.cells_dict["tetra"]   # (M, 4)

N = points.shape[0]
M = cells.shape[0]
print(f"节点数: {N}, 四面体单元数: {M}")

# ------------------------------
# 2. 单元刚度矩阵计算函数
# ------------------------------
def tetra_volume(pts):
    """计算四面体体积"""
    v1 = pts[1] - pts[0]
    v2 = pts[2] - pts[0]
    v3 = pts[3] - pts[0]
    return abs(np.dot(v1, np.cross(v2, v3))) / 6.0

def tetra_stiffness(pts):
    """✅ 永远正确：不挑节点顺序，Gmsh 网格直接用"""
    v01 = pts[1] - pts[0]
    v02 = pts[2] - pts[0]
    v03 = pts[3] - pts[0]
    V = np.abs(np.dot(v01, np.cross(v02, v03))) / 6.0

    M = np.array([pts[1]-pts[0], pts[2]-pts[0], pts[3]-pts[0]]).T
    invM = np.linalg.inv(M)

    gradN = np.zeros((4,3))
    gradN[0] = -invM[0] - invM[1] - invM[2]
    gradN[1] = invM[0]
    gradN[2] = invM[1]
    gradN[3] = invM[2]

    return V * (gradN @ gradN.T)

# ------------------------------
# 3. 组装全局矩阵
# ------------------------------
print("组装全局刚度矩阵...")
K = lil_matrix((N, N))
f = np.zeros(N)

for i, elem in enumerate(cells):
    if i % 5000 == 0:
        print(f"  处理单元 {i}/{M}")
    pts = points[elem]
    Ke = tetra_stiffness(pts)
    for ii, gi in enumerate(elem):
        for jj, gj in enumerate(elem):
            K[gi, gj] += Ke[ii, jj]

# ------------------------------
# 4. 施加 Dirichlet 边界条件 (底面 0V, 顶面 1V)
# ------------------------------
print("施加边界条件...")
z = points[:, 2]
tol = 1e-8
bottom_dofs = np.where(np.abs(z) < tol)[0]
top_dofs    = np.where(np.abs(z - 1.0) < tol)[0]

print(f"底面节点数: {len(bottom_dofs)}, 顶面节点数: {len(top_dofs)}")

big = 1e15
for dof in bottom_dofs:
    K[dof, :] = 0
    K[dof, dof] = big
    f[dof] = big * 0.0

for dof in top_dofs:
    K[dof, :] = 0
    K[dof, dof] = big
    f[dof] = big * 1.0

# 转换为 CSR 格式以提高求解效率
K_csr = K.tocsr()

# ------------------------------
# 5. 求解线性系统
# ------------------------------
print("求解线性方程组...")
phi = spsolve(K_csr, f)
print("求解完成")

# ------------------------------
# 6. 保存结果到 VTK 文件
# ------------------------------
print("保存结果到 reference_result.vtk")
meshio.write_points_cells(
    "reference_result.vtk",
    points,
    [("tetra", cells)],
    point_data={"phi": phi},
    file_format="vtk",
    binary=False   # 可选 ASCII 方便查看
)

# ------------------------------
# 7. 输出中心线附近电势（验证）
# ------------------------------
tol_center = 0.05
center = (np.abs(points[:,0]-0.5) < tol_center) & (np.abs(points[:,1]-0.5) < tol_center)
z_center = points[center, 2]
phi_center = phi[center]

idx = np.argsort(z_center)
z_sorted = z_center[idx]
phi_sorted = phi_center[idx]

print("\n中心线电势分布 (x≈0.5, y≈0.5):")
step = max(1, len(z_sorted)//10)
for i in range(0, len(z_sorted), step):
    print(f"z = {z_sorted[i]:.4f}, φ = {phi_sorted[i]:.6f}")

# 线性拟合
coeff = np.polyfit(z_sorted, phi_sorted, 1)
print(f"\n拟合结果: φ = {coeff[0]:.6f} * z + {coeff[1]:.6f}")
print(f"理论值: φ = 1.0 * z + 0.0")