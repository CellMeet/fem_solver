"""边界条件管理器（稳定版）"""

from .bc_condition import BCType


def find_boundary_nodes(mesh, tol=1e-3):
    """自动寻找外边界节点"""
    nodes = []
    for node in mesh.nodes:
        if (node.x < tol or node.x > 1 - tol or
            node.y < tol or node.y > 1 - tol):
            nodes.append(node.id)
    return nodes


def apply_dirichlet_to_node(A, b, node_id, value):
    """正确的Dirichlet施加（行+列消元）"""
    big = 1e15

    # 删除行
    keys_row = [(i, j) for (i, j) in A.keys() if i == node_id and j != node_id]
    for key in keys_row:
        del A[key]

    # 删除列（关键）
    keys_col = [(i, j) for (i, j) in A.keys() if j == node_id and i != node_id]
    for key in keys_col:
        del A[key]

    # 设置对角
    A[(node_id, node_id)] = big
    b[node_id] = big * value


class BCManager:
    def __init__(self):
        self.dirichlet_nodes = []

    def add_dirichlet_node(self, node_id, value):
        self.dirichlet_nodes.append((node_id, value))

    def apply_all(self, A, b, mesh):
        # 应用Dirichlet
        for node_id, val in self.dirichlet_nodes:
            apply_dirichlet_to_node(A, b, node_id, val)

        # ⭐ 自动加 pin node（防止奇异）
        if len(self.dirichlet_nodes) == 0:
            apply_dirichlet_to_node(A, b, 0, 0.0)

        return A, b