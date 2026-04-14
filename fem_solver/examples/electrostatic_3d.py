import sys
import os
import numpy as np
from scipy.sparse import lil_matrix
from scipy.sparse.linalg import spsolve, cg, eigsh
from scipy.sparse import diags

# ==========================
# 路径设置
# ==========================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fem_solver.meshing.gmsh_mesher import GmshMesher
from fem_solver.material.material import ConstantMaterial
from fem_solver.postprocess.writer import VTKWriter

# ==========================
# 稀疏求解器（带诊断）
# ==========================
class DirectSolver:
    def solve(self, A_sparse, b, bc, n):
        fixed = list(bc.keys())
        free = [i for i in range(n) if i not in fixed]

        A_ff = A_sparse[free, :][:, free]
        A_fc = A_sparse[free, :][:, fixed]

        b_f = b[free]
        bc_vals = np.array([bc[i] for i in fixed])

        rhs = b_f - A_fc @ bc_vals

        u = np.zeros(n)
        u[free] = spsolve(A_ff, rhs)

        for i in fixed:
            u[i] = bc[i]
        return u, A_ff, rhs

# ==========================
# 组装器
# ==========================
class Assembler:
    def __init__(self, mesh):
        self.mesh = mesh
        self.n = mesh.node_count
        self.A = lil_matrix((self.n, self.n))

    def assemble(self, material, source_func, print_first_n=2):
        self.A = lil_matrix((self.n, self.n))
        b = np.zeros(self.n)
        bad = 0
        valid_elem = 0

        for elem in self.mesh.elements:
            if len(elem.nodes) != 4:
                continue

            Ke = elem.compute_stiffness_matrix(material)

            if np.all(Ke == 0):
                bad += 1
                continue

            if valid_elem < print_first_n:
                print(f"\n===== 单元 {elem.id} (全局ID) =====")
                ids_global = [n.id for n in elem.nodes]
                print(f"全局ID: {ids_global}")
                coords = np.array([[n.x, n.y, n.z] for n in elem.nodes])
                print("节点坐标:")
                for i, (n, coord) in enumerate(zip(elem.nodes, coords)):
                    print(f"  局部{i} (全局{n.id}): ({coord[0]:.6f}, {coord[1]:.6f}, {coord[2]:.6f})")
                print("刚度矩阵 Ke =")
                print(np.array2string(Ke, precision=6, suppress_small=True))

                # 校验
                M = np.hstack((np.ones((4, 1)), coords))
                try:
                    invM = np.linalg.inv(M)
                    V = abs(np.linalg.det(M)) / 6.0
                    grad = invM[1:4, :].T
                    center = np.mean(coords, axis=0)
                    c = material.get_c(*center)
                    Ke_check = c * V * (grad @ grad.T)
                    if np.allclose(Ke, Ke_check, atol=1e-12):
                        print("校验通过：Ke 与校验值一致。")
                    else:
                        print("⚠️ 警告：Ke 与校验值不一致！")
                except np.linalg.LinAlgError:
                    print("校验失败：矩阵奇异")

            valid_elem += 1
            fe = elem.compute_load_vector(source_func)
            ids = [n.id for n in elem.nodes]
            for i, gi in enumerate(ids):
                b[gi] += fe[i]
                for j, gj in enumerate(ids):
                    self.A[gi, gj] += Ke[i, j]

        print(f"\n跳过坏单元数: {bad}")
        print(f"有效单元数: {valid_elem}")
        return self.A.tocsc(), b

# ==========================
# 主程序
# ==========================
def main():
    print("🚀 生成网格...")
    mesh_file = GmshMesher.create_box_mesh(0, 1, 0, 1, 0, 1, mesh_size=0.3)
    mesh = GmshMesher.load_mesh(mesh_file)

    print(f"节点数: {mesh.node_count}, 单元数: {mesh.element_count}")

    material = ConstantMaterial("air", 1.0)
    def source_func(x, y, z): return 0.0

    print("\n🔧 组装刚度矩阵...")
    assembler = Assembler(mesh)
    A, b = assembler.assemble(material, source_func, print_first_n=2)

    asym = (A - A.T).nnz
    print(f"不对称元素数: {asym}")

    # 边界条件
    bc = {}
    for node in mesh.nodes:
        if abs(node.z) < 1e-12:
            bc[node.id] = 0.0
        elif abs(node.z - 1.0) < 1e-12:
            bc[node.id] = 1.0

    print(f"边界条件总数: {len(bc)}")

    # 直接求解
    solver = DirectSolver()
    phi_direct, A_ff, rhs = solver.solve(A, b, bc, mesh.node_count)

    # 共轭梯度对比
    print("\n⚙️ 尝试共轭梯度法求解...")
    phi_cg = np.zeros(mesh.node_count)
    fixed = list(bc.keys())
    free = [i for i in range(mesh.node_count) if i not in fixed]
    diag_Aff = A_ff.diagonal()
    diag_Aff[diag_Aff == 0] = 1.0
    M = diags(1.0 / diag_Aff)
    u_cg_free, info = cg(A_ff, rhs, M=M, rtol=1e-14, atol=1e-14)
    if info == 0:
        print("CG 收敛成功")
    else:
        print(f"CG 未收敛，退出码: {info}")
    phi_cg[free] = u_cg_free
    for i in fixed:
        phi_cg[i] = bc[i]

    # 条件数估算
    try:
        lambda_max = eigsh(A_ff, k=1, which='LM', return_eigenvectors=False)[0]
        lambda_min = eigsh(A_ff, k=1, which='SM', return_eigenvectors=False)[0]
        cond_est = lambda_max / lambda_min
        print(f"估算条件数 (max/min eig): {cond_est:.2e}")
    except Exception as e:
        print(f"条件数估算失败: {e}")

    # Patch Test 验证
    exact = np.array([n.z for n in mesh.nodes])
    error_direct = phi_direct - exact
    L2_direct = np.sqrt(np.mean(error_direct**2))
    max_direct = np.max(np.abs(error_direct))

    error_cg = phi_cg - exact
    L2_cg = np.sqrt(np.mean(error_cg**2))
    max_cg = np.max(np.abs(error_cg))

    print(f"\n🧪 直接求解器: L2误差 = {L2_direct:.3e}, 最大误差 = {max_direct:.3e}")
    print(f"🧪 CG 求解器:   L2误差 = {L2_cg:.3e}, 最大误差 = {max_cg:.3e}")

    print("\n内部节点抽样 (前5个):")
    count = 0
    for node in mesh.nodes:
        if node.id in bc:
            continue
        print(f"  id={node.id:3d}  z={node.z:.4f}  φ_direct={phi_direct[node.id]:.8f}  φ_cg={phi_cg[node.id]:.8f}  err_direct={error_direct[node.id]:.3e}")
        count += 1
        if count >= 5:
            break

    VTKWriter.write(mesh, phi_direct, "result_direct.vtk")
    print("\n💾 结果已写入 result_direct.vtk")
    print("✅ 完成")

if __name__ == "__main__":
    main()