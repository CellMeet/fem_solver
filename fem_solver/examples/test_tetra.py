import numpy as np
import sys
import os
# 当前文件所在目录：fem_solver/examples
current_dir = os.path.dirname(os.path.abspath(__file__))
# 项目根目录：向上两级
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 假设您的 TetrahedronElement 和 Node 类已可导入
from fem_solver.core.node import Node
from fem_solver.core.element import TetrahedronElement
from fem_solver.material.material import ConstantMaterial

def test_regular_tetrahedron():
    # 直角四面体：体积 = 1/6，边向量沿坐标轴
    # 节点顺序：A(0,0,0), B(1,0,0), C(0,1,0), D(0,0,1)
    nodes = [
        Node(0, 0.0, 0.0, 0.0),
        Node(1, 1.0, 0.0, 0.0),
        Node(2, 0.0, 1.0, 0.0),
        Node(3, 0.0, 0.0, 1.0)
    ]
    elem = TetrahedronElement(0, nodes)
    material = ConstantMaterial("test", 1.0)

    Ke = elem.compute_stiffness_matrix(material)

    print("计算得到的刚度矩阵 Ke =")
    print(np.array2string(Ke, precision=6, suppress_small=True))

    # 理论解析解（对于该直角四面体，材料系数 c=1）
    # 形函数梯度：
    # N0 = 1 - x - y - z  → ∇N0 = [-1,-1,-1]^T
    # N1 = x              → ∇N1 = [1,0,0]^T
    # N2 = y              → ∇N2 = [0,1,0]^T
    # N3 = z              → ∇N3 = [0,0,1]^T
    # 体积 V = 1/6
    # K_ij = V * (∇N_i · ∇N_j)
    # 手工计算得：
    # K = 1/6 * [[ 3, -1, -1, -1],
    #            [-1,  1,  0,  0],
    #            [-1,  0,  1,  0],
    #            [-1,  0,  0,  1]]
    V = 1.0 / 6.0
    K_theory = V * np.array([
        [ 3, -1, -1, -1],
        [-1,  1,  0,  0],
        [-1,  0,  1,  0],
        [-1,  0,  0,  1]
    ])

    print("\n理论刚度矩阵 K_theory =")
    print(np.array2string(K_theory, precision=6, suppress_small=True))

    diff = Ke - K_theory
    print("\n差值 Ke - K_theory =")
    print(np.array2string(diff, precision=3, suppress_small=True))
    print(f"最大绝对误差: {np.max(np.abs(diff)):.2e}")

if __name__ == "__main__":
    test_regular_tetrahedron()