import sys
import os
import numpy as np
from collections import defaultdict

# ==========================
# 路径
# ==========================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# ==========================
# FEM 模块
# ==========================
from fem_solver.meshing.gmsh_mesher import GmshMesher
from fem_solver.material.material import ConstantMaterial
from fem_solver.postprocess.writer import VTKWriter


# ==========================================================
# 直接求解器（稳定版）
# ==========================================================
class DirectSolver:
    def solve(self, A_sparse, b, bc, n):

        A = np.zeros((n, n))

        for (i, j), v in A_sparse.items():
            A[i, j] = v

        fixed = list(bc.keys())
        free = [i for i in range(n) if i not in fixed]

        A_ff = A[np.ix_(free, free)]
        A_fc = A[np.ix_(free, fixed)]

        b_f = b[free]
        bc_v = np.array([bc[i] for i in fixed])

        u = np.zeros(n)
        u[free] = np.linalg.solve(A_ff, b_f - A_fc @ bc_v)

        for i in fixed:
            u[i] = bc[i]

        return u


# ==========================================================
# Assembler（写在 main 内部）
# ==========================================================
class Assembler:
    def __init__(self, mesh):
        self.mesh = mesh
        self.n = mesh.node_count
        self.A = defaultdict(float)

    def assemble(self, material, source_func):

        self.A.clear()
        b = np.zeros(self.n)

        bad = 0

        for elem in self.mesh.elements:

            if len(elem.nodes) != 4:
                continue

            Ke = elem.compute_stiffness_matrix(material)

            # ❗过滤退化单元
            if np.all(Ke == 0):
                bad += 1
                continue

            fe = elem.compute_load_vector(source_func)

            ids = [n.id for n in elem.nodes]

            for i, gi in enumerate(ids):
                b[gi] += fe[i]
                for j, gj in enumerate(ids):
                    self.A[(gi, gj)] += Ke[i, j]

        print(f"⚠️ 跳过坏单元数: {bad}")
        print(f"刚度矩阵非零项数: {len(self.A)}")

        return self.A, b


# ==========================================================
# 主程序
# ==========================================================
def main():

    print("🚀 生成网格...")
    mesh_file = GmshMesher.create_box_mesh(0, 1, 0, 1, 0, 1, mesh_size=0.1)
    mesh = GmshMesher.load_mesh(mesh_file)

    print(f"节点数: {mesh.node_count}, 单元数: {mesh.element_count}")

    material = ConstantMaterial("air", 1.0)

    def source_func(x, y, z):
        return 0.0

    # ==========================
    # 组装
    # ==========================
    print("\n🔧 组装刚度矩阵...")
    assembler = Assembler(mesh)
    A, b = assembler.assemble(material, source_func)

    # ==========================
    # Dirichlet BC (φ = z)
    # ==========================
    bc = {}

    for node in mesh.nodes:
        if abs(node.z - 0.0) < 1e-8:
            bc[node.id] = 0.0
        elif abs(node.z - 1.0) < 1e-8:
            bc[node.id] = 1.0

    print(f"Dirichlet 节点数: {len(bc)}")

    # ==========================
    # 求解
    # ==========================
    solver = DirectSolver()
    phi = solver.solve(A, b, bc, mesh.node_count)

    # ==========================
    # 误差分析
    # ==========================
    exact = np.array([n.z for n in mesh.nodes])
    error = np.abs(phi - exact)

    print("\n================================================")
    print("平均误差:", np.mean(error))
    print("最大误差:", np.max(error))
    print("L2误差:", np.linalg.norm(error))
    print("================================================")

    print("\n前20个节点结果：")
    for i in range(20):
        print(f"{i:3d}  z={mesh.nodes[i].z:.4f}  φ={phi[i]:.6f}  err={error[i]:.3e}")

    # ==========================
    # 输出
    # ==========================
    VTKWriter.write(mesh, phi, "result.vtk")
    print("\n💾 已写出 result.vtk")
    print("✅ 完成")


# ==========================================================
if __name__ == "__main__":
    main()