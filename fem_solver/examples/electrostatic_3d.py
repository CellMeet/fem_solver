import sys
import os
import numpy as np

# --------------------------
# 路径设置
# --------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --------------------------
# 导入模块
# --------------------------
from fem_solver.meshing.gmsh_mesher import GmshMesher
from fem_solver.material.material import ConstantMaterial
from fem_solver.assembly.assembler import Assembler
from fem_solver.solver.direct_solver import DirectSolver
from fem_solver.postprocess.writer import VTKWriter, TextWriter


# ==============================================================================
# ✅ Dirichlet 消元（完整版，含 RHS 修正）
# ==============================================================================
def apply_dirichlet_elimination(A, b, bc, n_nodes):
    A = A.copy()

    for i, value in bc.items():

        # ⭐ Step 1: RHS 修正（核心！）
        for j in range(n_nodes):
            if (j, i) in A:
                b[j] -= A[(j, i)] * value

        # ⭐ Step 2: 清行
        for j in range(n_nodes):
            A[(i, j)] = 0.0

        # ⭐ Step 3: 清列
        for j in range(n_nodes):
            A[(j, i)] = 0.0

        # ⭐ Step 4: 对角 + RHS
        A[(i, i)] = 1.0
        b[i] = value

    return A, b


# ==============================================================================
# 主程序
# ==============================================================================
def main():

    print("🚀 生成网格...")
    mesh_file = GmshMesher.create_box_mesh(0, 1, 0, 1, 0, 1, mesh_size=0.05)
    solver_mesh = GmshMesher.load_mesh(mesh_file)

    print(f"节点数: {solver_mesh.node_count}, 单元数: {solver_mesh.element_count}")

    n_nodes = solver_mesh.node_count

    # --------------------------
    # 材料
    # --------------------------
    material = ConstantMaterial("air", c=1.0)

    def source_func(x, y, z):
        return 0.0

    # --------------------------
    # 装配
    # --------------------------
    print("🔧 组装刚度矩阵...")
    assembler = Assembler(solver_mesh)
    A, _, b = assembler.assemble(material, source_func)

    # ⭐ 保存原始矩阵（用于 Patch Test）
    A_raw = A.copy()
    b_raw = b.copy()

    # --------------------------
    # Dirichlet BC（φ = z）
    # --------------------------
    bc = {}

    for node in solver_mesh.nodes:
        bc[node.id] = node.z

    print(f"Dirichlet节点数: {len(bc)}")

    # --------------------------
    # 施加边界条件
    # --------------------------
    print("📌 应用 Dirichlet 边界...")
    A, b = apply_dirichlet_elimination(A, b, bc, n_nodes)

    # --------------------------
    # 使用自定义求解器求解
    # --------------------------
    print("🧮 使用 DirectSolver 求解...")
    solver = DirectSolver()
    phi = solver.solve(A, b)   # A 是字典格式，b 是列表

    # --------------------------
    # 误差分析
    # --------------------------
    max_error = 0.0
    avg_error = 0.0

    for node in solver_mesh.nodes:
        exact = node.z
        numerical = phi[node.id]

        err = abs(numerical - exact)
        max_error = max(max_error, err)
        avg_error += err

    avg_error /= n_nodes

    # --------------------------
    # 🧪 PATCH TEST（必须用原始矩阵）
    # --------------------------
    print("\n🧪 PATCH TEST")

    test_phi = np.array([
        node.x + node.y + node.z
        for node in solver_mesh.nodes
    ])

    # ⭐ 用原始矩阵！
    A_test = np.zeros((n_nodes, n_nodes))
    for (i, j), val in A_raw.items():
        A_test[i, j] = val

    res = A_test @ test_phi

    print("残差 max:", np.max(np.abs(res)))
    print("残差 L2:", np.linalg.norm(res))

    # --------------------------
    # 自检：矩阵对称性
    # --------------------------
    print("\n🔍 矩阵对称性检查")
    for (i, j) in A_raw:
        if abs(A_raw[(i, j)] - A_raw.get((j, i), 0.0)) > 1e-10:
            print("❌ NOT symmetric!", i, j)
            break
    else:
        print("✅ 矩阵对称")

    # --------------------------
    # 输出结果
    # --------------------------
    print("\n" + "=" * 50)
    print("🔍 FEM 测试结果")
    print("=" * 50)
    print("解析解 φ = z")
    print(f"平均误差: {avg_error:.3e}")
    print(f"最大误差: {max_error:.3e}")
    print("=" * 50)

    # --------------------------
    # 输出文件
    # --------------------------
    print("💾 写出结果...")
    VTKWriter.write(solver_mesh, phi, "result.vtk")
    TextWriter.write(solver_mesh, phi, "result.txt")

    print("✅ 完成！")


# ==============================================================================
# 入口
# ==============================================================================
if __name__ == "__main__":
    main()