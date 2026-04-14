import numpy as np

class Element:
    def __init__(self, id, nodes):
        self.id = id
        self.nodes = nodes
        self.n_nodes = len(nodes)


class TetrahedronElement(Element):

    def compute_stiffness_matrix(self, material):
        coords = np.array([[n.x, n.y, n.z] for n in self.nodes])
        # 体积坐标法：构建系数矩阵并求逆
        M = np.ones((4, 4))
        M[:, 1:] = coords
        try:
            invM = np.linalg.inv(M)
        except np.linalg.LinAlgError:
            return np.zeros((4, 4))
        V = abs(np.linalg.det(M)) / 6.0
        if V < 1e-14:
            return np.zeros((4, 4))
        # 形函数梯度矩阵：invM[1:4, :] 的转置，形状 (4,3)
        grad = invM[1:4, :].T
        center = np.mean(coords, axis=0)
        c = material.get_c(*center)
        Ke = c * V * (grad @ grad.T)
        return Ke

    def compute_load_vector(self, source_func):
        p = np.array([[n.x, n.y, n.z] for n in self.nodes])
        A, B, C, D = p

        J = np.column_stack((B - A, C - A, D - A))
        detJ = np.linalg.det(J)
        V = abs(detJ) / 6.0

        # 单元中心坐标
        center = np.mean(p, axis=0)
        f = source_func(*center)

        # 线性四面体载荷向量均分
        return np.full(4, f * V / 4.0)