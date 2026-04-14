"""
统一有限元单元：Triangle (T3) + Tetrahedron (T4)
标准 FEM reference formulation（已修复 patch test 问题）
"""

import numpy as np


# ------------------------------------------------------------------------------
# 基类
# ------------------------------------------------------------------------------
class Element:
    def __init__(self, id, nodes):
        self.id = id
        self.nodes = nodes
        self.n_nodes = len(nodes)

    def get_centroid(self):
        coords = np.array([[n.x, n.y, getattr(n, "z", 0.0)] for n in self.nodes])
        return np.mean(coords, axis=0)


# ------------------------------------------------------------------------------
# 2D 三角形单元 (T3)
# ------------------------------------------------------------------------------
class TriangleElement(Element):
    def __init__(self, id, nodes):
        if len(nodes) != 3:
            raise ValueError("TriangleElement必须3个节点")
        super().__init__(id, nodes)

    def get_area(self):
        x = np.array([n.x for n in self.nodes])
        y = np.array([n.y for n in self.nodes])

        return 0.5 * abs(
            x[0]*(y[1]-y[2]) +
            x[1]*(y[2]-y[0]) +
            x[2]*(y[0]-y[1])
        )

    def compute_stiffness_matrix(self, material):
        x = np.array([n.x for n in self.nodes])
        y = np.array([n.y for n in self.nodes])

        J = np.array([
            [x[1]-x[0], x[2]-x[0]],
            [y[1]-y[0], y[2]-y[0]]
        ])

        detJ = np.linalg.det(J)
        if abs(detJ) < 1e-14:
            return np.zeros((3, 3))

        invJ = np.linalg.inv(J)

        # reference gradient (correct)
        grad_ref = np.array([
            [-1, -1],
            [ 1,  0],
            [ 0,  1]
        ])

        # ✔ 正确 mapping（关键修复）
        grad_phys = (invJ.T @ grad_ref.T).T

        c = material.get_c(*self.get_centroid())
        area = abs(detJ) / 2.0

        Ke = np.zeros((3, 3))

        for i in range(3):
            for j in range(3):
                Ke[i, j] = c * area * np.dot(grad_phys[i], grad_phys[j])

        return Ke

    def compute_mass_matrix(self, material):
        area = self.get_area()
        rho = material.get_rho(*self.get_centroid())

        Me = np.ones((3, 3)) * (rho * area / 12.0)
        np.fill_diagonal(Me, rho * area / 6.0)

        return Me

    def compute_load_vector(self, source_func):
        cx, cy = self.get_centroid()
        f = source_func(cx, cy)

        area = self.get_area()
        return np.full(3, f * area / 3.0)


# ------------------------------------------------------------------------------
# 3D 四面体单元 (T4)
# ------------------------------------------------------------------------------
class TetrahedronElement(Element):
    def __init__(self, id, nodes):
        if len(nodes) != 4:
            raise ValueError("TetrahedronElement必须4个节点")
        super().__init__(id, nodes)

    def get_volume(self):
        p = np.array([[n.x, n.y, n.z] for n in self.nodes])
        return abs(np.linalg.det(np.column_stack((p[1]-p[0],
                                                  p[2]-p[0],
                                                  p[3]-p[0])))) / 6.0

    def compute_stiffness_matrix(self, material):
        p = np.array([[n.x, n.y, n.z] for n in self.nodes])
        p0, p1, p2, p3 = p

        J = np.column_stack((p1 - p0,
                              p2 - p0,
                              p3 - p0))

        detJ = np.linalg.det(J)
        if abs(detJ) < 1e-14:
            return np.zeros((4, 4))

        invJ = np.linalg.inv(J)

        # reference gradients (correct)
        grad_ref = np.array([
            [-1, -1, -1],
            [ 1,  0,  0],
            [ 0,  1,  0],
            [ 0,  0,  1]
        ])

        # ✔ 修复：正确 FEM mapping（核心）
        grad_phys = (invJ.T @ grad_ref.T).T

        eps = material.get_c(*self.get_centroid())
        V = abs(detJ) / 6.0

        Ke = np.zeros((4, 4))

        for i in range(4):
            for j in range(4):
                Ke[i, j] = eps * np.dot(grad_phys[i], grad_phys[j]) * V

        return Ke

    def compute_mass_matrix(self, material):
        V = self.get_volume()
        rho = material.get_rho(*self.get_centroid())

        Me = np.ones((4, 4)) * (rho * V / 20.0)
        np.fill_diagonal(Me, rho * V / 10.0)

        return Me

    def compute_load_vector(self, source_func):
        cx, cy, cz = self.get_centroid()
        f = source_func(cx, cy, cz)

        V = self.get_volume()
        return np.full(4, f * V / 4.0)