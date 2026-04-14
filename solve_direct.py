import meshio
import numpy as np
from scipy.sparse import lil_matrix, csr_matrix
from scipy.sparse.linalg import spsolve

print("1. 读取网格...")
msh = meshio.read("box.msh")
points = msh.points
cells = msh.cells_dict["tetra"]
print(f"  节点数: {points.shape[0]}, 单元数: {cells.shape[0]}")

def tetra_volume(pts):
    v1 = pts[1] - pts[0]
    v2 = pts[2] - pts[0]
    v3 = pts[3] - pts[0]
    return abs(np.dot(v1, np.cross(v2, v3))) / 6.0

def tetra_stiffness(pts):
    """
    ⭐ 标准 P1 tetra FEM stiffness matrix
    """

    x0, x1, x2, x3 = pts

    J = np.column_stack((x1 - x0, x2 - x0, x3 - x0))
    detJ = np.linalg.det(J)

    if abs(detJ) < 1e-14:
        return np.zeros((4, 4))

    invJ = np.linalg.inv(J)

    # reference element gradients
    grad_ref = np.array([
        [-1, -1, -1],
        [ 1,  0,  0],
        [ 0,  1,  0],
        [ 0,  0,  1]
    ])

    grad_phys = grad_ref @ invJ.T

    K = np.zeros((4, 4))

    for i in range(4):
        for j in range(4):
            K[i, j] = np.dot(grad_phys[i], grad_phys[j]) * abs(detJ) / 6.0

    return K

print("2. 组装全局矩阵...")
n_nodes = points.shape[0]
K = lil_matrix((n_nodes, n_nodes))
f = np.zeros(n_nodes)

for i, elem in enumerate(cells):
    if i % 1000 == 0:
        print(f"  处理单元 {i}/{len(cells)}")
    pts = points[elem]
    Ke = tetra_stiffness(pts)
    for ii, gi in enumerate(elem):
        for jj, gj in enumerate(elem):
            K[gi, gj] += Ke[ii, jj]

print("3. 施加边界条件...")
z = points[:, 2]
tol = 1e-8
bottom_dofs = np.where(np.abs(z) < tol)[0]
top_dofs = np.where(np.abs(z - 1.0) < tol)[0]
print(f"  底面节点数: {len(bottom_dofs)}, 顶面节点数: {len(top_dofs)}")

big_number = 1e15
for dof in bottom_dofs:
    K[dof, :] = 0
    K[dof, dof] = big_number
    f[dof] = big_number * 0.0
for dof in top_dofs:
    K[dof, :] = 0
    K[dof, dof] = big_number
    f[dof] = big_number * 1.0

print("4. 转换矩阵格式...")
K_csr = K.tocsr()

print("5. 求解线性系统...")
phi = spsolve(K_csr, f)
print("  求解完成")

print("6. 保存结果...")
meshio.write_points_cells(
    "reference_result_ascii.vtk",
    points,
    [("tetra", cells)],
    point_data={"phi": phi},
    file_format="vtk",
    binary=False   # 关键参数
)
print("结果已保存至 reference_result.vtk")