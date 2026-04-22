import sys
import os
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import spsolve

# ==========================
# 路径设置
# ==========================
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from fem_solver.meshing.gmsh_mesher import GmshMesher
from fem_solver.postprocess.writer import VTKWriter

# ==========================
# 修正后的组装器 (带内置数学校验)
# ==========================
class Assembler:
    def __init__(self, mesh):
        self.mesh = mesh
        self.n = mesh.node_count
        # 建立 ID 到 0-based 索引的映射 (防止 Gmsh ID 从1开始导致的偏移)
        self.id_map = {node.id: i for i, node in enumerate(self.mesh.nodes)}

    def assemble(self, material_c=1.0):
        # 使用更高效的 COO 格式准备数据，最后转 CSR
        rows = []
        cols = []
        data = []
        b = np.zeros(self.n)
        
        valid_tet_count = 0

        for elem in self.mesh.elements:
            # 1. 严格过滤：只处理 4 节点单元
            if len(elem.nodes) != 4:
                continue
            
            # 2. 获取节点坐标 (4x3 矩阵)
            coords = np.array([[n.x, n.y, n.z] for n in elem.nodes])
            
            # 3. 计算单元刚度矩阵 Ke (使用标准线性四面体公式)
            # 构建 M = [[1, x0, y0, z0], ...]
            M = np.hstack((np.ones((4, 1)), coords))
            try:
                detM = np.linalg.det(M)
                V = abs(detM) / 6.0  # 四面体体积
                
                if V < 1e-15: continue # 过滤退化单元

                invM = np.linalg.inv(M)
                # 形状函数的梯度在 invM 的第 2, 3, 4 行 (对应 x, y, z)
                # grad 维度为 (4, 3)，每一行是对应节点的 (dN/dx, dN/dy, dN/dz)
                grad = invM[1:4, :].T 
                
                # Ke = c * V * (grad @ grad.T)
                Ke = material_c * V * (grad @ grad.T)
                
            except np.linalg.LinAlgError:
                continue

            # 4. 组装
            valid_tet_count += 1
            g_indices = [self.id_map[n.id] for n in elem.nodes]
            
            for i in range(4):
                for j in range(4):
                    rows.append(g_indices[i])
                    cols.append(g_indices[j])
                    data.append(Ke[i, j])

        # 转换为压缩稀疏矩阵
        A = csr_matrix((data, (rows, cols)), shape=(self.n, self.n))
        print(f"✅ 组装完成: 有效四面体 {valid_tet_count} 个")
        return A, b

# ==========================
# 主程序
# ==========================
def main():
    print("🚀 步骤 1: 生成网格...")
    mesh_file = "box.msh"
    # 如果文件不存在则生成
    GmshMesher.create_box_mesh(0, 1, 0, 1, 0, 1, mesh_size=0.3, filename=mesh_file)
    mesh = GmshMesher.load_mesh(mesh_file)
    print(f"节点数: {mesh.node_count}, 原始单元数: {mesh.element_count}")

    print("\n🔧 步骤 2: 组装全局矩阵...")
    assembler = Assembler(mesh)
    A, b = assembler.assemble(material_c=1.0)

    print("\n⚖️ 步骤 3: 施加边界条件 (Patch Test: z=0 -> 0, z=1 -> 1)")
    phi = np.zeros(mesh.node_count)
    id_map = assembler.id_map
    
    fixed_indices = []
    fixed_vals = []
    
    for node in mesh.nodes:
        idx = id_map[node.id]
        if abs(node.z) < 1e-12:
            phi[idx] = 0.0
            fixed_indices.append(idx)
            fixed_vals.append(0.0)
        elif abs(node.z - 1.0) < 1e-12:
            phi[idx] = 1.0
            fixed_indices.append(idx)
            fixed_vals.append(1.0)

    all_indices = np.arange(mesh.node_count)
    free_indices = np.setdiff1d(all_indices, fixed_indices)
    
    # 划分矩阵：A_ff * u_f = b_f - A_fc * u_c
    A_ff = A[free_indices, :][:, free_indices]
    A_fc = A[free_indices, :][:, fixed_indices]
    
    rhs = b[free_indices] - A_fc @ np.array(fixed_vals)

    print(f"求解线性方程组 (自由度: {len(free_indices)})...")
    u_free = spsolve(A_ff, rhs)
    phi[free_indices] = u_free

    # ==========================
    # 结果分析
    # ==========================
    exact = np.array([node.z for node in mesh.nodes])
    error = phi - exact
    max_err = np.max(np.abs(error))
    l2_err = np.sqrt(np.mean(error**2))

    print("\n📊 Patch Test 结果:")
    print(f"   最大绝对误差: {max_err:.3e}")
    print(f"   L2 均方误差: {l2_err:.3e}")

    if max_err < 1e-10:
        print("🎉 恭喜！误差达到机器精度，求解器逻辑完全正确。")
    else:
        print("⚠️ 误差依然较大，请检查单元节点顺序或 Gmsh 加载逻辑。")

    print("\n内部节点抽样:")
    count = 0
    for i, node in enumerate(mesh.nodes):
        idx = id_map[node.id]
        if idx not in fixed_indices and count < 5:
            print(f"  Node ID:{node.id:<3} z={node.z:.3f} Phi={phi[idx]:.6f} Error={error[idx]:.3e}")
            count += 1

    VTKWriter.write(mesh, phi, "result_patch_test.vtk")
    print("\n✅ 完成")

if __name__ == "__main__":
    main()